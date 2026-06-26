import re
import os
from collections import Counter
import sys
import argparse

from transformers import BertModel
from transformers import BertTokenizer

import torch
from torch import nn
import torch.optim as optim
import numpy as np
import random

from booknlp.common.pipelines import Token, Entity
from booknlp.english.litbank_quote import QuoteTagger
from booknlp.english.name_coref import NameCoref

from booknlp.english.bert_qa import QuotationAttribution

random.seed(1)
np.random.seed(1)
torch.manual_seed(1)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("using device", device)


class BERTCorefTagger(nn.Module):

	def __init__(self, gender_cats, freeze_bert=False, base_model=None, pronominalCorefOnly=True):
		super(BERTCorefTagger, self).__init__()

		modelName=base_model
		modelName=re.sub("^coref_", "", modelName)
		modelName=re.sub("-v\d.*$", "", modelName)

		matcher=re.search(".*-(\d+)_H-(\d+)_A-.*", modelName)
		bert_dim=0
		modelSize=0

		self.num_layers=0
		if matcher is not None:
			self.num_layers=min(4, int(matcher.group(1)))
			bert_dim=int(matcher.group(2))

			modelSize=self.num_layers*bert_dim

		assert bert_dim != 0

		self.pronominalCorefOnly=pronominalCorefOnly

		self.tokenizer = BertTokenizer.from_pretrained(modelName, do_lower_case=False, do_basic_tokenize=False)
		self.bert = BertModel.from_pretrained(modelName)

		self.tokenizer.add_tokens(["[CAP]"], special_tokens=True)
		self.bert.resize_token_embeddings(len(self.tokenizer))

		self.bert.eval()

		self.vec_get_distance_bucket=np.vectorize(self.get_distance_bucket)

		if freeze_bert:
			for param in self.bert.parameters():
				param.requires_grad = False

		self.distance_embeddings = nn.Embedding(43, 20)
		self.speaker_embeddings = nn.Embedding(3, 20)
		self.nested_embeddings = nn.Embedding(2, 20)
		self.gender_embeddings = nn.Embedding(3, 20)
		self.width_embeddings = nn.Embedding(12, 20)
		self.quote_embeddings = nn.Embedding(3, 20)

		self.hidden_dim=bert_dim
		self.attention1 = nn.Linear(self.hidden_dim, self.hidden_dim)
		self.attention2 = nn.Linear(self.hidden_dim, 1)
		self.mention_mention1 = nn.Linear( (3 * self.hidden_dim + 20 + 20) * 3 + 20 + 20 + 20 + 20, 150)
		self.mention_mention2 = nn.Linear(150, 150)
		self.mention_mention3 = nn.Linear(150, 1)

		self.unary1 = nn.Linear(3 * self.hidden_dim + 20 + 20, 150)
		self.unary2 = nn.Linear(150, 150)
		self.unary3 = nn.Linear(150, 1)

		self.drop_layer_020 = nn.Dropout(p=0.2)
		self.tanh = nn.Tanh()

		self.gender_cats=gender_cats
		self.gender_expressions={}
		for val in self.gender_cats:
			cat='/'.join(val)
			self.gender_expressions[cat]={}
			for w in cat.split("/"):
				self.gender_expressions[cat][w]=1

		self.conflicting_genders={}
		for cat in self.gender_expressions:
			self.conflicting_genders[cat]={}
			for alt_cat in self.gender_expressions:
				if cat != alt_cat:
					for w in self.gender_expressions[alt_cat]:
						if w not in self.gender_expressions[cat]:
							self.conflicting_genders[cat][w]=1


	def get_mention_reps(self, input_ids=None, attention_mask=None, starts=None, ends=None, index=None, widths=None, quotes=None, matrix=None, transforms=None, doTrain=True):

		starts=starts.to(device)
		ends=ends.to(device)
		widths=widths.to(device)

		quotes=quotes.to(device)

		input_ids = input_ids.to(device)
		attention_mask = attention_mask.to(device)
		transforms = transforms.to(device)

		# matrix specifies which token positions (cols) are associated with which mention spans (row)
		matrix=matrix.to(device) # num_sents x max_ents x max_words

		# index specifies the location of the mentions in each sentence (which vary due to padding)
		index=index.to(device)

		_, pooled_outputs, sequence_outputs = self.bert(input_ids, token_type_ids=None, attention_mask=attention_mask, output_hidden_states=True, return_dict=False)

		all_layers = sequence_outputs[-1]
		embeds=torch.matmul(transforms,all_layers)

		average=torch.matmul(matrix, embeds)

		###########
		# ATTENTION OVER MENTION
		###########

		attention_weights=self.attention2(self.tanh(self.attention1(embeds))) # num_sents x max_words x 1
		attention_weights=torch.exp(attention_weights)
		
		attx=attention_weights.squeeze(-1).unsqueeze(1).expand_as(matrix)
		summer=attx*matrix

		val=matrix*summer # num_sents x max_ents x max_words
		
		val=val/torch.sum(1e-8+val,dim=2).unsqueeze(-1)

		attended=torch.matmul(val, embeds) # num_sents x max_ents x 2 * hidden_dim

		attended=attended.view(-1,self.hidden_dim)

		embeds=embeds.contiguous()
		position_output=embeds.view(-1, self.hidden_dim)
		
		# starts = token position of beginning of mention in flattened token list
		start_output=torch.index_select(position_output, 0, starts)
		# ends = token position of end of mention in flattened token list
		end_output=torch.index_select(position_output, 0, ends)

		# index = index of entity in flattened list of attended mention representations
		mentions=torch.index_select(attended, 0, index)

		average=average.view(-1,self.hidden_dim)
		averaged_mentions=torch.index_select(average, 0, index)

		width_embeds=self.width_embeddings(widths)

		quote_embeds=self.quote_embeddings(quotes)

		span_representation=torch.cat((start_output, end_output, mentions, width_embeds, quote_embeds), 1)

		if doTrain:
			return span_representation
		else:
			# detach tensor from computation graph at test time or memory will blow up
			return span_representation.detach()


	def assign_quotes_to_entity(self, entities):
		# For training, assign quotes to the nearest gold mention
		for idx, entity in enumerate(entities):
			dists=[]
			if entity.in_quote:
				for j in range(len(entities)):
					if not entities[j].in_quote and entities[j].entity_id == entity.quote_eid:
						dists.append((abs(j-idx), j))

				for dist, j in sorted(dists, reverse=False):
					entity.quote_mention=j
					break
			


	def add_property(self, entity_properties, cand_assignment, mention, ref_genders):

		if cand_assignment not in entity_properties:
			entity_properties[cand_assignment]={}

		entity_properties[cand_assignment]["ner_cat"]=mention.ner_cat
		

	def is_compatible(self, cand_mention, eid, entity_properties, mention, ref_genders, score):

		# If we've already given a referential gender to a candidate in a previous step using global 
		# information, respect that global inference when linking pronouns rather than relying on local coref to do it.
		if len(mention.text.split(" ")) == 1:
			term=mention.text.lower()

			if eid in ref_genders:
				cat=ref_genders[eid]["argmax"]
				if term in self.conflicting_genders[cat]:
					return False

		# Don't allow links between mentions with different NER categories
		if eid in entity_properties and mention.ner_cat in entity_properties[eid]:
			if mention.ner_cat != entity_properties[eid]["ner_cat"]:
				return False

		return True

	def get_non_quote_cands(self, first, idx, entities):

		# entities not in quotes can only refer back to other entities not in quotes
		dists=[]

		for i in range(first, idx):
			if entities[i].in_quote == False:
				dists.append(i)

		return np.array(dists), list(reversed(np.arange(len(dists))))


	def get_closest_entities(self, first, idx, entities, top=10):

		# entities in quotes can refer back to *any* entity (in quote or outside) or up to 10 entities outside quotes ahead
		dists=list(np.arange(first, idx))

		ent_dist=list(reversed(np.arange(len(dists))))

		k=1
		for i in range(idx+1, min(idx+1+top, len(entities))):
			
			if entities[i].in_quote == False:
				dists.append(i)
				ent_dist.append(-k)
				k+=1

		return np.array(dists), ent_dist

	def forward(self, matrix, index, existing=None, truth=None, token_positions=None, starts=None, ends=None, widths=None, input_ids=None, attention_mask=None, transforms=None, entities=None, ref_genders={}):
		
		doTrain=False
		if truth is not None:
			doTrain=True

		zeroTensor=torch.FloatTensor([0]).to(device)

		entity_properties={}

		if existing is not None:
			for idx, val in enumerate(existing):
				e=entities[idx]
				if val != -1 and val is not None:
					self.add_property(entity_properties, val, e, ref_genders)

		all_starts=None
		all_ends=None

		span_representation=None

		all_all=[]
		cur=0
		for b in range(len(matrix)):

			quotes=[]
			for entity in entities[cur:cur+len(starts[b])]:
				if entity.in_quote:
					quotes.append(1)
				else:
					quotes.append(0)
			cur+=len(starts[b])

			quotes=torch.LongTensor(quotes)

			span_reps=self.get_mention_reps(input_ids=input_ids[b], attention_mask=attention_mask[b], starts=starts[b], ends=ends[b], index=index[b], widths=widths[b], quotes=quotes, transforms=transforms[b], matrix=matrix[b], doTrain=doTrain)
			
			if b == 0:
				span_representation=span_reps
				all_starts=starts[b]
				all_ends=ends[b]

			else:

				span_representation=torch.cat((span_representation, span_reps), 0)
	
				all_starts=torch.cat((all_starts, starts[b]), 0)
				all_ends=torch.cat((all_ends, ends[b]), 0)

		all_starts=all_starts.to(device)
		all_ends=all_ends.to(device)
		
		num_mentions,=all_starts.shape

		running_loss=0

		curid=-1

		if existing is not None:
			for r in existing:
				if r > curid:
					curid=r

		curid+=1

		assignments=[None]*len(entities)

		if truth is not None:
			for idx, entity in enumerate(entities):
				assignments[idx]=entity.entity_id

		seen={}

		ch=0

		token_positions=np.array(token_positions)

		mention_index=np.arange(num_mentions)

		unary_scores=self.unary3(self.tanh(self.drop_layer_020(self.unary2(self.tanh(self.drop_layer_020(self.unary1(span_representation)))))))

		# process entities outside of quotes first

		for inQuoteVal in [False, True]:

			for i in range(num_mentions):
				
				entity=entities[i]

				if entity.in_quote != inQuoteVal:
					continue

				# if the mention has already been resolved through name coref, skip it
				if not doTrain and existing is not None and existing[i] != -1:
					assignments[i]=existing[i]
					continue

				# if the mention is a pronoun and we're only doing pronominal coref, skip it
				# (assign the mention a unique entity ID, to be clustered later)
				elif not doTrain and entity.proper != "PRON" and self.pronominalCorefOnly:

					assignment=curid
					curid+=1
					assignments[i]=assignment

					continue				

				if i == 0:
					# the first mention must start a new entity; this doesn't affect training (since the loss must be 0) so we can skip it.
					if not doTrain:
						
						if existing is None or (existing is not None and existing[i] == -1):
							assignment=curid
							curid+=1
							assignments[i]=assignment
						else:

							assignments[i]=existing[i]
					
					continue

				MAX_PREVIOUS_MENTIONS=20

				first=max(0,i-MAX_PREVIOUS_MENTIONS)

				cands_idx=None
				if inQuoteVal == False:
					# entities not in quotes can only refer back to other entities not in quotes
					cands_idx, ent_dist=self.get_non_quote_cands(first, i, entities)
				else:
					# entities in quotes can refer back to *any* entity (in quote or outside) or up to 10 entities outside quotes ahead
					cands_idx, ent_dist=self.get_closest_entities(first, i, entities)

				cands_idx=cands_idx[-MAX_PREVIOUS_MENTIONS:]
				ent_dist=ent_dist[-MAX_PREVIOUS_MENTIONS:]


				preds=None

				# if there are no candidates, then don't bother training, but create a new entity ID if predicting
				if len(cands_idx) == 0:

					if truth is None:
						
						if existing is None or (existing is not None and existing[i] == -1):
							assignment=curid
							curid+=1
							assignments[i]=assignment
						else:
							assignments[i]=existing[i]
					
					continue

				else:

					targets=span_representation[cands_idx]
					cp=span_representation[i].expand_as(targets)
					
					dists=[]
					nesteds=[]

					# force 1st person pronouns in quotes to co-refer with the quote speaker
					if entity.quote_mention is not None and assignments[entity.quote_mention ] is not None and (entity.text.lower() == "i" or entity.text.lower() == "me" or entity.text.lower() == "my" or entity.text.lower() == "myself") and entity.in_quote:
						assignments[i]=assignments[entity.quote_mention]
						continue

					same_speaker=[]
					for e in cands_idx:
						if not entities[i].in_quote:
							same_speaker.append(2)
						else:

							# the candidates for every mention in a quote have already been resolved
							# (either candidates outside of quotes, or earlier mentions within quotes)
							# check if the *speaker* of the quote the mention is embedded within is coreferent with that candidate

							if entities[i].quote_mention is None:
								same_speaker.append(2)
							else:
								attribution_assignment=assignments[entities[i].quote_mention]

								if assignments[e] == attribution_assignment:
									same_speaker.append(1)
								else:
									same_speaker.append(0)


					same_speaker_embeds=self.speaker_embeddings(torch.LongTensor(same_speaker).to(device))

					# get distance in mentions
					dists=self.vec_get_distance_bucket(ent_dist)
					dists=torch.LongTensor(dists).to(device)
					distance_embeds=self.distance_embeddings(dists)

					# is the current mention nested within a previous one?

					nest1=[]
					nest2=[]
					for cand in cands_idx:
						if entity.global_start >= entities[cand].global_start and entity.global_end < entities[cand].global_end:
							nest1.append(1)
						else:
							nest1.append(0)
						if entities[cand].global_start >= entity.global_start and entities[cand].global_end < entity.global_end:
							nest2.append(1)
						else:
							nest2.append(0)

					nesteds_embeds=self.nested_embeddings(torch.LongTensor(nest1).to(device))
					nesteds_embeds2=self.nested_embeddings(torch.LongTensor(nest2).to(device))

					elementwise=cp*targets
					concat=torch.cat((cp, targets, elementwise, distance_embeds, nesteds_embeds, nesteds_embeds2, same_speaker_embeds), 1)

					preds=self.mention_mention3(self.tanh(self.drop_layer_020(self.mention_mention2(self.tanh(self.drop_layer_020(self.mention_mention1(concat)))))))

					preds=preds + unary_scores[i] + unary_scores[cands_idx]

					preds=preds.squeeze(-1)

				if doTrain:
		
					# zero is the score for the dummy antecedent/new entity
					preds=torch.cat((preds, zeroTensor))
		
					golds_sum=0.
					preds_sum=torch.logsumexp(preds, 0)

					if len(truth[i]) == 0:
						golds_sum=0.
					else:
						golds=torch.index_select(preds, 0, torch.LongTensor(truth[i]).to(device))
						golds_sum=torch.logsumexp(golds, 0)

					# want to maximize (golds_sum-preds_sum), so minimize (preds_sum-golds_sum)
					diff=preds_sum-golds_sum

					running_loss+=diff

				else:

					if existing is not None and existing[i] != -1:
						assignments[i]=existing[i]

					elif entity.proper != "PRON" and self.pronominalCorefOnly:

						assignment=curid
						curid+=1
						assignments[i]=assignment

						continue

					else:

						assignment=None

						if i == 0 or len(cands_idx) == 0:
							assignment=curid
							curid+=1
						else:
							arg_sorts=torch.argsort(preds, descending=True)
							k=0
							while k < len(arg_sorts):
								cand_idx=arg_sorts[k]
								if preds[cand_idx] > 0:
									score=preds[cand_idx]
									
									cand_assignment=assignments[cands_idx[cand_idx]]
									cand_mention=entities[cands_idx[cand_idx]]
									if cand_assignment is None:
										print("problem!", cands_idx[cand_idx], preds[cand_idx], cand_assignment, i, inQuoteVal, assignments, torch.sort(preds, descending=True))
										sys.exit(1)
									
									if self.is_compatible(cand_mention, cand_assignment, entity_properties, entity, ref_genders, score):
										assignment=cand_assignment
										ch+=1
										self.add_property(entity_properties, cand_assignment, entity, ref_genders)
										break

								else:
									assignment=curid
									curid+=1
									break

								k+=1

						if assignment is None:
							# print("adding default new entity due to lack of compatibility", i, assignment)
							assignment=curid
							curid+=1

						assignments[i]=assignment
				

		if truth is not None:
			return running_loss
		else:
			return assignments


	def get_mention_width_bucket(self, dist):
		if abs(dist) < 10:
			return abs(dist) + 1

		return 11

	def get_distance_bucket(self, dist):

		if dist < 30:
			return dist + 10

		if dist < 40:
			return 41

		return 42

	def print_conll(self, name, sents, all_ents, assignments, out, token_maps):

		doc_id, part_id=name

		mapper=[]
		idd=0
		for ent in all_ents:
			mapper_e=[]
			for e in ent:
				mapper_e.append(idd)
				idd+=1
			mapper.append(mapper_e)

		out.write("#begin document (%s); part %s\n" % (doc_id, part_id))
		
		cur_tok=0
		tok_id=0

		for s_idx, sent in enumerate(sents):
			ents=all_ents[s_idx]
			for w_idx, word in enumerate(sent):

				if w_idx == 0 or w_idx == len(sent)-1:
					continue

				label=[]
				for idx, entity in enumerate(ents):
					start=entity.start
					end=entity.end
					if start == w_idx and end == w_idx:
						eid=assignments[mapper[s_idx][idx]]
						label.append("(%s)" % eid)
					elif start == w_idx:
						eid=assignments[mapper[s_idx][idx]]
						label.append("(%s" % eid)
					elif end == w_idx:
						eid=assignments[mapper[s_idx][idx]]
						label.append("%s)" % eid)

				out.write("%s\t%s\t%s\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s\n" % (doc_id, part_id, tok_id, word, '|'.join(label)))
				tok_id+=1
				cur_tok+=1

				if cur_tok in token_maps[doc_id]:
					out.write("\n")
					tok_id=0

		out.write("#end document\n")


	def read_toks(self, filename):

		tok_sent_idx=0
		lastSent=None
		toks=[]
		with open(filename) as file:
			file.readline()
			for line in file:
				cols=line.rstrip().split("\t")
				parID=int(cols[0])
				sentenceID=int(cols[1])
				tokenID=int(cols[2])
				text=cols[7]
				pos=cols[10]
				lemma=cols[9]
				deprel=cols[12]
				dephead=int(cols[6])
				ner=cols[11]
				startByte=int(cols[3])

				if sentenceID != lastSent:
					tok_sent_idx=0

				tok=Token(parID, sentenceID, tok_sent_idx, tokenID, text, pos, None, lemma, deprel, dephead, ner, startByte)

				tok_sent_idx+=1
				lastSent=sentenceID
				toks.append(tok)

		return toks


	def get_matrix(self, list_of_entities, max_words, max_ents):

		matrix=np.zeros((max_ents, max_words))
		for idx, entity in enumerate(list_of_entities):
			for i in range(entity.start, entity.end+1):
				matrix[idx,i]=1
		return matrix


	def get_data(self, doc, ents, max_ents, max_words, batchsize=128):

		token_positions=[]
		ent_spans=[]
		persons=[]
		inquotes=[]

		batch_matrix=[]
		matrix=[]

		max_words_batch=[]
		max_ents_batch=[]

		max_w=1
		max_e=1

		sent_count=0
		for idx, sent in enumerate(doc):
			
			if len(sent) > max_w:
				max_w=len(sent)
			if len(ents[idx]) > max_e:
				max_e = len(ents[idx])

			sent_count+=1

			if sent_count == batchsize:
				max_words_batch.append(max_w)
				max_ents_batch.append(max_e)
				sent_count=0
				max_w=0
				max_e=0

		if sent_count > 0:
			max_words_batch.append(max_w)
			max_ents_batch.append(max_e)

		batch_count=0
		for idx, sent in enumerate(doc):
			matrix.append(self.get_matrix(ents[idx], max_words_batch[batch_count], max_ents_batch[batch_count]))

			if len(matrix) == batchsize:
				batch_matrix.append(torch.FloatTensor(np.array(matrix)))
				matrix=[]
				batch_count+=1

		if len(matrix) > 0:
			batch_matrix.append(torch.FloatTensor(np.array(matrix)))


		batch_index=[]
		batch_quotes=[]

		batch_ent_spans=[]

		index=[]
		abs_pos=0
		sent_count=0

		b=0
		for idx, sent_ents in enumerate(ents):

			for i in range(len(sent_ents)):
				index.append(sent_count*max_ents_batch[b] + i)
				#s,e,inQuote=sent[i]
				entity=sent_ents[i]
				token_positions.append(idx)
				ent_spans.append(entity.end-entity.start)
				phrase=' '.join(doc[idx][entity.start:entity.end+1])

				inquotes.append(entity.in_quote)


			abs_pos+=len(doc[idx])

			sent_count+=1

			if sent_count == batchsize:
				batch_index.append(torch.LongTensor(index))
				batch_quotes.append(torch.LongTensor(inquotes))
				batch_ent_spans.append(ent_spans)

				index=[]
				inquotes=[]
				ent_spans=[]
				sent_count=0
				b+=1

		if sent_count > 0:
			batch_index.append(torch.LongTensor(index))
			batch_quotes.append(torch.LongTensor(inquotes))
			batch_ent_spans.append(ent_spans)

		all_masks=[]
		all_transforms=[]
		all_data=[]

		batch_masks=[]
		batch_transforms=[]
		batch_data=[]

		# get ids and pad sentence
		for sent in doc:
			tok_ids=[]
			input_mask=[]
			transform=[]

			all_toks=[]
			n=0
			for idx, word in enumerate(sent):
				toks=self.tokenizer.tokenize(word)
				all_toks.append(toks)
				n+=len(toks)


			cur=0
			for idx, word in enumerate(sent):

				toks=all_toks[idx]
				ind=list(np.zeros(n))
				for j in range(cur,cur+len(toks)):
					ind[j]=1./len(toks)
				cur+=len(toks)
				transform.append(ind)

				tok_id=self.tokenizer.convert_tokens_to_ids(toks)
				assert len(tok_id) == len(toks)
				tok_ids.extend(tok_id)

				input_mask.extend(np.ones(len(toks)))

				token=word.lower()

			all_masks.append(input_mask)
			all_data.append(tok_ids)
			all_transforms.append(transform)

			if len(all_masks) == batchsize:
				batch_masks.append(all_masks)
				batch_data.append(all_data)
				batch_transforms.append(all_transforms)

				all_masks=[]
				all_data=[]
				all_transforms=[]

		if len(all_masks) > 0:
			batch_masks.append(all_masks)
			batch_data.append(all_data)
			batch_transforms.append(all_transforms)


		for b in range(len(batch_data)):

			max_len = max([len(sent) for sent in batch_data[b]])

			for j in range(len(batch_data[b])):
				
				blen=len(batch_data[b][j])

				for k in range(blen, max_len):
					batch_data[b][j].append(0)
					batch_masks[b][j].append(0)
					for z in range(len(batch_transforms[b][j])):
						batch_transforms[b][j][z].append(0)

				for k in range(len(batch_transforms[b][j]), max_words_batch[b]):
					batch_transforms[b][j].append(np.zeros(max_len))

			batch_data[b]=torch.LongTensor(batch_data[b])
			batch_transforms[b]=torch.FloatTensor(np.array(batch_transforms[b]))
			batch_masks[b]=torch.FloatTensor(batch_masks[b])
			
		tok_pos=0
		starts=[]
		ends=[]
		widths=[]

		batch_starts=[]
		batch_ends=[]
		batch_widths=[]

		sent_count=0
		b=0
		for idx, sent_ents in enumerate(ents):

			for i in range(len(sent_ents)):

				entity=sent_ents[i]

				starts.append(tok_pos+entity.start)
				ends.append(tok_pos+entity.end)
				widths.append(self.get_mention_width_bucket(entity.end-entity.start))

			sent_count+=1
			tok_pos+=max_words_batch[b]

			if sent_count == batchsize:
				batch_starts.append(torch.LongTensor(starts))
				batch_ends.append(torch.LongTensor(ends))
				batch_widths.append(torch.LongTensor(widths))

				starts=[]
				ends=[]
				widths=[]
				tok_pos=0
				sent_count=0
				b+=1

		if sent_count > 0:
			batch_starts.append(torch.LongTensor(starts))
			batch_ends.append(torch.LongTensor(ends))
			batch_widths.append(torch.LongTensor(widths))


		return batch_matrix, batch_index, token_positions, ent_spans, batch_starts, batch_ends, batch_widths, batch_data, batch_masks, batch_transforms, batch_quotes

	def get_ant_labels(self, all_doc_sents, all_doc_ents, all_quotes):

		max_words=0
		max_ents=0
		mention_id=0

		big_ents={}

		doc_antecedent_labels=[]
		quote_antecedent_labels=[]

		all_ents=[]

		big_doc_ents=[]

		for idx, sent in enumerate(all_doc_sents):
			if len(sent) > max_words:
				max_words=len(sent)

			this_sent_ents=[]
			all_sent_ents=sorted(all_doc_ents[idx], key=lambda x: (x.start, x.end))
			all_ents.extend(all_sent_ents)

			if len(all_sent_ents) > max_ents:
				max_ents=len(all_sent_ents)

			for entity in all_sent_ents:
				this_sent_ents.append(entity)

			big_doc_ents.append(this_sent_ents)


		for idx, entity in enumerate(all_ents):


			MAX_PREVIOUS_MENTIONS=20

			first=max(0,idx-MAX_PREVIOUS_MENTIONS)

			if entity.in_quote == False:
				cands_idx, _=self.get_non_quote_cands(first, idx, all_ents)

			else:
				cands_idx, _=self.get_closest_entities(first, idx, all_ents)
				
			cands_idx=cands_idx[-MAX_PREVIOUS_MENTIONS:]

			vals=[]
			for c_idx, cand_idx in enumerate(cands_idx):
				if entity.entity_id == all_ents[cand_idx].entity_id:
					vals.append(c_idx)

			doc_antecedent_labels.append(vals)

		return doc_antecedent_labels, big_doc_ents, max_words, max_ents, quote_antecedent_labels

	def read_conll(self, filename, quotes={}):

		
		sentence_breaks={}

		docid=None
		partID=None

		all_docids=[]
		all_sents=[]
		all_ents=[]
		all_antecedent_labels=[]
		all_max_words=[]
		all_max_ents=[]
		all_doc_names=[]

		all_named_ents=[]

		all_quotes=[]


		# for one doc
		all_doc_sents=[]
		all_doc_ents=[]
		all_doc_named_ents=[]
		all_doc_quotes=[]

		# for one sentence
		sent=[]
		ents={}
		sent_quotes=[]
		sent.append("[CLS]")

		# sentence ID in original CoNLL file
		sid=0

		# word ID within sentence in original CoNLL file
		wid=0

		# global token ID within document
		global_id=-1

		cur_batch_sid=0

		named_ents=[]
		cur_tokens=0
		max_allowable_tokens=425
		cur_tid=0
		open_count=0

		doc_count=0
		lastQuoteStart=None
		doc_quotes=[]

		with open(filename, encoding="utf-8") as file:


			for line in file:
				if line.startswith("#begin document"):
					doc_count+=1
					cur_batch_sid=tok_id=0

					global_id=-1
					lastQuoteStart=None
					adjusted_quotes=[]
					doc_quotes=[]

					inQuote=False, None, None, None, None, None

					all_doc_ents=[]
					all_doc_sents=[]
					all_doc_quotes=[]

					all_doc_named_ents=[]

					open_ents={}
					open_named_ents={}

					ents={}
					sent_quotes=[]
					named_ents=[]
					sent=["[CLS]"]
					cur_tokens=0
					cur_tid=0
					open_count=0

					sid=0
					wid=0

					docid=None
					matcher=re.match("#begin document \((.*)\); part (.*)$", line.rstrip())
					if matcher != None:
						docid=matcher.group(1)
						partID=matcher.group(2)

					all_docids.append(docid)

					sentence_breaks[docid]={}

				elif line.startswith("#end document"):

					all_quotes.append(doc_quotes)

					if len(sent) > 1:
						sent.append("[SEP]")
						all_doc_sents.append(sent)

						# transform ents dict to list
						ents=list(ents.values())
						ents=sorted(ents, key=lambda x: (x.start, x.end))

						named_ents=sorted(named_ents, key=lambda x: (x[0], x[1]))

						all_doc_ents.append(ents)
						all_doc_named_ents.append(named_ents)
						all_doc_quotes.append(sent_quotes)

						doc_quotes.append(adjusted_quotes)


					all_sents.append(all_doc_sents)

					doc_antecedent_labels, big_ents, max_words, max_ents, quote_antecedent_labels=self.get_ant_labels(all_doc_sents, all_doc_ents, all_doc_quotes)

					all_ents.append(big_ents)

					all_named_ents.append(all_doc_named_ents)

					all_antecedent_labels.append(doc_antecedent_labels)
					all_max_words.append(max_words+1)
					all_max_ents.append(max_ents+1)
					
					all_doc_names.append((docid,partID))

				else:

					parts=re.split("\s+", line.rstrip())

					if len(parts) < 2:
						sid+=1
						wid=0
						sentence_breaks[docid][tok_id]=1
						continue
					# new sentence
					if (cur_tokens >= max_allowable_tokens and open_count == 0):
			
						sent.append("[SEP]")
						all_doc_sents.append(sent)

						ents=list(ents.values())
						ents=sorted(ents, key=lambda x: (x.start, x.end))

						named_ents=sorted(named_ents, key=lambda x: (x[0], x[1]))
						sent_quotes=sorted(sent_quotes, key=lambda x: (x[0], x[1]))

						all_doc_ents.append(ents)
						all_doc_named_ents.append(named_ents)

						doc_quotes.append(adjusted_quotes)

						all_doc_quotes.append(sent_quotes)

						ents={}
						named_ents=[]
						sent_quotes=[]
						adjusted_quotes=[]
						sent=[]
						sent.append("[CLS]")

						cur_tokens=0

						cur_tid=0

						cur_batch_sid+=1

						if len(parts) < 2:
							continue

					# +1 to account for initial [CLS]
					tid=cur_tid+1

					token=parts[3]

					if token[0].lower() != token[0]:
						token="[CAP] " + token.lower()

					global_id+=1
					tok_id+=1
					orig_sent_id=parts[1]
					orig_token_id=parts[2]

					coref=parts[-1].split("|")
					b_toks=self.tokenizer.tokenize(token)
					cur_tokens+=len(b_toks)
					cur_tid+=1


					if docid in quotes and sid in quotes[docid]:

						# see if this word ends a quote
						for start_sid, start_wid, end_sid, end_wid, eid in quotes[docid][sid]["END"]:
							if sid == end_sid and wid == end_wid:
								inQuote=False, None, None, None, None, None
								adjusted_quotes.append((lastQuoteStart[0], lastQuoteStart[1], cur_batch_sid, tid))
			
						# see if this word starts a new quote
						for start_sid, start_wid, end_sid, end_wid, eid in quotes[docid][sid]["START"]:		
							if sid == start_sid and wid == start_wid:
								inQuote=True, eid, start_sid, start_wid, end_sid, end_wid
								lastQuoteStart=cur_batch_sid, tid

					wid+=1
					sent.append(token)

					for c in coref:
						if c.startswith("(") and c.endswith(")"):
							c=re.sub("\(", "", c)
							c=int(re.sub("\)", "", c))

							ents[(tid,tid)]=Entity(tid, tid, in_quote=inQuote[0], quote_eid=inQuote[1], quote_id=len(adjusted_quotes), entity_id=c, text=' '.join(sent[tid:tid+1]))
							ents[(tid,tid)].global_start=global_id
							ents[(tid,tid)].global_end=global_id
							
						elif c.startswith("("):
							c=int(re.sub("\(", "", c))

							if c not in open_ents:
								open_ents[c]=[]
							open_ents[c].append((tid, global_id))
							open_count+=1

						elif c.endswith(")"):
							c=int(re.sub("\)", "", c))

							assert c in open_ents

							start_tid, start_global_id=open_ents[c].pop()
							open_count-=1

							ents[(start_tid,tid)]=Entity(start_tid, tid, in_quote=inQuote[0], quote_eid=inQuote[1], quote_id=len(adjusted_quotes), entity_id=c, text=' '.join(sent[start_tid:tid+1]))
							ents[(start_tid,tid)].global_start=start_global_id
							ents[(start_tid,tid)].global_end=global_id

					ner=parts[10].split("|")

					for c in ner:

						if c.startswith("(") and c.endswith(")"):
							c=re.sub("\(", "", c)
							c=(re.sub("\)", "", c))

							if (tid, tid) in ents:
								ner_parts=c.split("_")
								ents[(tid, tid)].ner_cat=ner_parts[1]
								ents[(tid, tid)].proper=ner_parts[0]

						elif c.startswith("("):
							c=(re.sub("\(", "", c))

							if c not in open_named_ents:
								open_named_ents[c]=[]
							open_named_ents[c].append(tid)

						elif c.endswith(")"):
							c=(re.sub("\)", "", c))

							assert c in open_named_ents

							start_tid=open_named_ents[c].pop()

							if (start_tid, tid) in ents:
								ner_parts=c.split("_")
								ents[(start_tid, tid)].ner_cat=ner_parts[1]
								ents[(start_tid, tid)].proper=ner_parts[0]

		return all_sents, all_ents, all_named_ents, all_antecedent_labels, all_max_words, all_max_ents, all_doc_names, sentence_breaks, all_quotes, all_docids



