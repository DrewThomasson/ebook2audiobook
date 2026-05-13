import torch
import re
import os
from booknlp.english.speaker_attribution import BERTSpeakerID
import numpy as np
import sys

PINK = '\033[95m'
ENDC = '\033[0m'

class QuotationAttribution:

	def __init__(self, modelFile):

		device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

		base_model=re.sub("google_bert", "google/bert", os.path.basename(modelFile))
		base_model=re.sub("\.model$", "", base_model)

		self.model = BERTSpeakerID(base_model=base_model)
		state_dict = torch.load(modelFile, map_location=device)
		# Filter out unexpected keys
		state_dict = {k: v for k, v in state_dict.items() if not k.startswith('bert.embeddings.position_ids')}
		self.model.load_state_dict(state_dict)
		self.model.to(device)
		self.model.eval()

	def tag(self, quotes, entities, tokens):

		def get_base(start, end, preds):
			if (start, end) in preds:
				s,e=preds[(start,end)]
				return get_base(s,e,preds)

			return start, end

		attributions=[None]*len(quotes)

		entity_by_position={}
		for idx, (start, end, cat, text) in enumerate(entities):
			entity_by_position[start, end]=idx

		texts, metas, positions, global_entity_positions, quote_indexes=self.get_representation(quotes, entities, tokens)

		x_batches, m_batches, y_batches, o_batches=self.model.get_batches(texts, metas)

		all_preds={}
		quote_chain={}

		idd=0
		prediction_id=0

		for x1, m1, y1, o1 in zip(x_batches, m_batches, y_batches, o_batches):
			y_pred = self.model.forward(x1, m1)
			orig, meta=o1
			predictions=torch.argmax(y_pred, axis=1).detach().cpu().numpy()
			for idx, pred in enumerate(predictions):

				global_quote_id=quote_indexes[prediction_id]

				prediction=pred[0]
				quote_start, quote_end=quotes[global_quote_id]
				sent=orig[idx]
				predval=y1["eid"][idx][prediction]

				if prediction >= len(meta[idx][1]):
					prediction=torch.argmax(y_pred[idx][:len(meta[idx][1])])

				g_start, g_end=global_entity_positions[prediction_id][prediction]

				cat,start, end, orig_text=positions[prediction_id][prediction]

				if cat == "QUOTE":
					g_start, g_end=get_base(start, end, quote_chain)
	
				if (g_start, g_end) in entity_by_position:
					quote_chain[quote_start, quote_end]=g_start, g_end
					attributions[prediction_id]=entity_by_position[g_start, g_end]
				else:
					print("Cannot resolve quotation")

				ent_start, ent_end, lab, ent_eid=meta[idx][1][prediction]

				if ' '.join(sent[ent_start:ent_end]) == "[PAR]":
					print("Problem!!!! Linked [PAR]")
					sys.exit(1)
							
				prediction_id+=1

		return attributions



	def get_representation(self, quotes, entities, tokens, doLowerCase=True):

		def convert_word(word):
			if word == "[ALTQUOTE]" or word == "[PAR]" or word == "[QUOTE]":
				word=word

			elif doLowerCase:
				if word[0].lower() != word[0]:
					word="[CAP] " + word.lower()
				else:
					word=word.lower()

			return word

		window=50

		texts=[]
		metas=[]
		positions=[]

		global_positions=[]

		quote_indexes=[]

		end_quotes={}

		# mark the tokens that are in quotes and index quotes by their final token
		in_quotes=np.zeros(len(tokens))
		for idx, (q_start, q_end) in enumerate(quotes):
			end_quotes[q_end]=idx
			for k in range(q_start, q_end+1):
				in_quotes[k]=1

		entities_by_start={}
		for start, end, cat, text in entities:
			ner_prop=cat.split("_")[0]
			ner_type=cat.split("_")[1]

			if ner_type != "PER":
				continue

			if start not in entities_by_start:
				entities_by_start[start]={}
			entities_by_start[start][end]=1

		for q_id, (start_tok, end_tok) in enumerate(quotes):

			start=end_tok
			count=0
			wp_tok_count=0
			# go back *window* tokens, not counting tokens that are in quotes
			lastPar=None
			while start >= 0 and count < window and wp_tok_count + len(self.model.tokenizer.tokenize(convert_word(tokens[start].text))) < 350:
				if in_quotes[start] == 0:
					count+=1
					wp_tok_count+=len(self.model.tokenizer.tokenize(convert_word(tokens[start].text)))
				if start in end_quotes:
					wp_tok_count+=1
				if tokens[start].paragraph_id != lastPar:
					wp_tok_count+=1
				lastPar=tokens[start].paragraph_id

				start-=1

			start+=1

			# go ahead *window* tokens, not counting tokens that are in quotes
			count=0
			end=end_tok
			while end < len(tokens) and count < window and wp_tok_count + len(self.model.tokenizer.tokenize(convert_word(tokens[end].text))) < 475:
				if in_quotes[end] == 0:
					count+=1
					wp_tok_count+=len(self.model.tokenizer.tokenize(convert_word(tokens[end].text)))
				if end in end_quotes:
					wp_tok_count+=1
				if tokens[end].paragraph_id != lastPar:
					wp_tok_count+=1
				lastPar=tokens[end].paragraph_id

				end+=1

			end-=1

			if end < end_tok+1:
				end=end_tok+1


			toks=[]
			cands=[]

			lastPar=None

			inserts=np.zeros(end-start, dtype=int)

			# the offset keeps track of the difference between the original token position and the resulting token position
			# (after the addition of [PAR], [QUOTE], [ALTQUOTE] pseudo-tokens, and the subtraction of tokens within quotations)
			offset=0
			
			# reverse map maps the resulting tokens (which include [PAR], [QUOTE] etc.) to the original position
			reverse_map=[]
			altquote_map={}

			for i in range(start, end):

				tok=tokens[i]

				# if we cross a sentence boundary, add a [PAR] pseudo-token and adjust the offset to keep track of these pseudo-tokens
				if tok.paragraph_id != lastPar and lastPar is not None:
					toks.append("[PAR]")
					reverse_map.append(i)
					offset+=1

				# if the token is not in a quotation, add it to the context representation
				# if it is in a quotation, decrease the offset
				if not in_quotes[i]:
					toks.append(tokens[i].text)
					reverse_map.append(i)
				else:
					offset-=1

				# if the token marks the end of the target quotation, add a [QUOTE] pseudo-token to represent the quotation in its entirety
				# (note we don't include any words from within the quotation itself)
				if i == end_tok:
					toks.append("[QUOTE]")
					reverse_map.append(i)
					offset+=1

				# if the token ends a *different* quote, add an [ALTQUOTE] pseudo-token to represent it
				elif i in end_quotes:
					altquote_map[len(toks)]=quotes[end_quotes[i]]
					toks.append("[ALTQUOTE]")
					reverse_map.append(i)
					offset+=1

					(q_start, q_end)=quotes[end_quotes[i]]
		
					# if the alt quote occurs *before* the target quote, add it as an attribution candidate
					if q_end < end_tok:
						quotepos=i+inserts[i-start-1]-start
						cands.append((min(abs(q_end-start_tok), abs(q_start-end_tok)), quotepos, quotepos, None, "QUOTE", None, None))

				# inserts keeps track of the difference between the original token position and final one
				inserts[i-start]=offset

				lastPar=tok.paragraph_id

			for entity_start in range(start, end):

				if entity_start in entities_by_start:
					# only allow entities not in quotes to be speaker candidates
					if in_quotes[entity_start] == 0:
						for entity_end in entities_by_start[entity_start]:
							# the candidate entity needs to be completely contained within the context
							if entity_end < end and entity_end+inserts[entity_end-start]-start < len(toks):
								# cand tuple values:
								# distance between the entity and the quotation (in original tokens)
								# entity start position (in final tokens)
								# entity end position (in final tokens)
								# entity ID (here unknown)
								# whether the candidate is an entity ("ENT") or alt quote ("QUOTE")
								# entity start position (in original tokens)
								# entity end position (in original tokens)
								# print(entity_start, start, entity_end, len(inserts))
								# print(inserts[entity_start-start])
								# print(inserts[entity_end-start])
								cands.append((min(abs(entity_end-start_tok), abs(entity_start-end_tok)), entity_start+inserts[entity_start-start]-start, entity_end+inserts[entity_end-start]-start, None, "ENT", entity_start, entity_end))

			tot_toks=0
			for tok in toks:
				tot_toks+=len(self.model.tokenizer.tokenize(convert_word(tok)))
			if tot_toks > 500:
				raise ValueError("Quotation window is unexpectedly long: %s" % tot_toks)

			labels=[]

			abs_positions=[]
			g_positions=[]

			if len(cands) > 0:
				# sort the candidates by their distance to the target quote and consider only the 10 closest
				cands=sorted(cands)
				for dist, s, e, eid, cat, global_start, global_end in cands[:10]:
					
					if ' '.join(toks[s:e+1]) == "[PAR]":
						# skip
						continue

					labels.append((int(s),int(e+1),0, eid))
					adjusted_s=reverse_map[s]
					adjusted_e=reverse_map[e]

					g_positions.append((global_start, global_end))

					if ' '.join(toks[s:e+1]) != "[ALTQUOTE]":
					# 	if ' '.join(toks[s:e+1])  != "[PAR]":
					# 		if ' '.join(toks[s:e+1]) != ' '.join([t.text for t in tokens[global_start:global_end+1]]):
					# 			print("ASSERTION\t#%s#%s#" % (' '.join(toks[s:e+1]), ' '.join([t.text for t in tokens[global_start:global_end+1]])))

						abs_positions.append(("ENT", global_start, global_end+1, ' '.join([t.text for t in tokens[global_start:global_end+1]])))
					else:
						abs_positions.append(("QUOTE", altquote_map[s][0], altquote_map[s][1], ' '.join([t.text for t in tokens[altquote_map[s][0]:altquote_map[s][1]]])))

				index=toks.index("[QUOTE]")
				texts.append(toks)
				metas.append((None, labels, index))
				positions.append(abs_positions)
				global_positions.append(g_positions)
				quote_indexes.append(q_id)

		return texts, metas, positions, global_positions, quote_indexes
	
