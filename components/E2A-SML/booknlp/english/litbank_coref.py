import torch, sys, re
import os

from booknlp.english.bert_coref_quote_pronouns import BERTCorefTagger
import numpy as np
from booknlp.common.pipelines import Entity
from booknlp.english.name_coref import NameCoref
import pkg_resources

class LitBankCoref:

	def __init__(self, modelFile, gender_cats, pronominalCorefOnly=True):

		device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

		base_model=re.sub("google_bert", "google/bert", os.path.basename(modelFile))
		base_model=re.sub("\.model$", "", base_model)

		self.model = BERTCorefTagger(gender_cats=gender_cats, freeze_bert=True, base_model=base_model, pronominalCorefOnly=pronominalCorefOnly)
		state_dict = torch.load(modelFile, map_location=device)
		# Filter out unexpected keys
		state_dict = {k: v for k, v in state_dict.items() if not k.startswith('bert.embeddings.position_ids')}
		self.model.load_state_dict(state_dict)
		self.model.to(device)
		self.model.eval()


	def tag(self, tokens, g_ents, refs, ref_gender, attributed_quotations, quotes):
		sentences, ents, max_words, max_ents=self.convert_data(tokens, g_ents)
		assignments,global_entities=self.test(sentences, ents, max_words, max_ents, refs, ref_gender, attributed_quotations, quotes)
		return assignments


	def test(self, test_doc, test_ents, max_words, max_ents, refs, ref_gender, attributed_quotations, quotes):

		global_entities=[]
		for ents in test_ents:
			global_entities.extend(ents)

		for ent in global_entities:
			if ent.in_quote:
				for idx, (q_start, q_end) in enumerate(quotes):
					if ent.global_start >= q_start and ent.global_start <= q_end:
						ent.quote_mention=attributed_quotations[idx]

		test_matrix, test_index, test_token_positions, test_ent_spans, test_starts, test_ends, test_widths, test_data, test_masks, test_transforms, test_quotes=self.model.get_data(test_doc, test_ents, max_ents, max_words)
		
		assignments=self.model.forward(test_matrix, test_index, existing=refs, token_positions=test_token_positions, starts=test_starts, ends=test_ends, widths=test_widths, input_ids=test_data, attention_mask=test_masks, transforms=test_transforms, ref_genders=ref_gender, entities=global_entities)
		
		aliasFile = pkg_resources.resource_filename(__name__, "data/aliases.txt")

		nameCoref=NameCoref(aliasFile)

		e_list=[]
		for ent in global_entities:
			e_list.append((ent.global_start, ent.global_end, "%s_%s" % (ent.proper, ent.ner_cat), ent.text))

		assignments=nameCoref.cluster_noms(e_list, assignments)

		for ass in assignments:
			if ass == -1:
				print(assignments)
				sys.exit(1)

		return assignments, global_entities

	def convert_data(self, tokens, entities):

		max_words=0
		max_ents=0

		sents=[]
		o_sents=[]
		sent=[]
		o_sent=[]
		lastSid=None
		max_sentence_length=500
		length=0
		mapper={}

		for tok in tokens:

			wptok=tok.text
			if wptok[0].lower() != wptok[0]:
				wptok="[CAP] " + wptok.lower()

			toks=self.model.tokenizer.tokenize(wptok)
			if lastSid is not None and (tok.sentence_id != lastSid or length + len(toks) > max_sentence_length):
				sents.append(sent)
				o_sents.append(o_sent)
				sent=[]
				o_sent=[]
				length=0
			
			sent.append(toks)
			o_sent.append(tok)

			lastSid=tok.sentence_id
			length+=len(toks)
		
		sents.append(sent)
		o_sents.append(o_sent)

		sentences=[]
		o_sentences=[]

		max_sentence_length=500

		sentence=[ "[CLS]" ]
		ents=[]
		o_sent=[]

		running_length=0

		for idx, sent in enumerate(sents):

			length=0
			for toks in sent:
				length+=len(toks)

			if length + running_length >= max_sentence_length:
				sentence.append("[SEP]")
				sentences.append(sentence)
				ents.append([])
				o_sentences.append(o_sent)
				running_length=1
				sentence=["[CLS]"]
				o_sent=[]

			running_length+=length

			for word in o_sents[idx]:
				mapper[word.token_id]=len(sentences), len(sentence)
				
				wptok=word.text
				if wptok[0].lower() != wptok[0]:
					wptok="[CAP] " + wptok.lower()

				sentence.append(wptok)

			o_sent.extend(o_sents[idx])


		if len(sentence) > 1:		
			sentence.append("[SEP]")
			ents.append([])
			o_sentences.append(o_sent)
			sentences.append(sentence)

		sents=o_sentences

		lastS=-1
		
		entities=sorted(entities)

		for (start, end, cat, text) in entities:
			sent_id, w_in_sent_id_start=mapper[tokens[start].token_id]
			e_sent_id, w_in_sent_id_end=mapper[tokens[end].token_id]

			# if sent_id != e_sent_id:
			# 	print(sent_id,e_sent_id, "crossing sentence boundaries!" )
			# if sent_id < lastS:
			# 	print(sent_id, lastS, "non-monotonic!")

			lastS=sent_id

			inQuote=0
			if tokens[start].inQuote or tokens[end].inQuote:
				inQuote=1
			

			ent=Entity(w_in_sent_id_start, w_in_sent_id_end, in_quote=inQuote, quote_eid=None, entity_id=None, text=text)
			ner_parts=cat.split("_")
			ent.ner_cat=ner_parts[1]
			ent.proper=ner_parts[0]
			ent.global_start=start
			ent.global_end=end

			ents[sent_id].append(ent)



		max_words=max(len(sentence) for sentence in sentences)
		max_ents=max(len(ent) for ent in ents)

		return sentences, ents, max_words, max_ents


