import sys
import spacy
import copy
from booknlp.common.pipelines import SpacyPipeline
from booknlp.english.entity_tagger import LitBankEntityTagger
from booknlp.english.gender_inference_model_1 import GenderEM
from booknlp.english.name_coref import NameCoref
from booknlp.english.litbank_coref import LitBankCoref
from booknlp.english.litbank_quote import QuoteTagger
from booknlp.english.bert_qa import QuotationAttribution
from os.path import join
import os
import json
from collections import Counter
from html import escape
import time
from pathlib import Path
import urllib.request 
import pkg_resources
import torch
import datetime

class EnglishBookNLP:

	def __init__(self, model_params):

		with torch.no_grad():

			start_time = time.time()

			print(model_params)

			spacy_model="en_core_web_sm"
			if "spacy_model" in model_params:
				spacy_model=model_params["spacy_model"]

			spacy_nlp = spacy.load(spacy_model, disable=["ner"])

			valid_keys=set("entity,event,supersense,quote,coref".split(","))
			
			pipes=model_params["pipeline"].split(",")

			self.gender_cats= [ ["he", "him", "his"], ["she", "her"], ["they", "them", "their"], ["xe", "xem", "xyr", "xir"], ["ze", "zem", "zir", "hir"] ] 

			if "referential_gender_cats" in model_params:
				self.gender_cats=model_params["referential_gender_cats"]

			home = str(Path.home())
			modelPath=os.path.join(home, "booknlp_models")
			if "model_path"  in model_params:			
				modelPath=model_params["model_path"]

			if not Path(modelPath).is_dir():
				Path(modelPath).mkdir(parents=True, exist_ok=True)

			if model_params["model"] == "big":
				entityName="entities_google_bert_uncased_L-6_H-768_A-12-v1.0.model"
				corefName="coref_google_bert_uncased_L-12_H-768_A-12-v1.0.model"
				quoteAttribName="speaker_google_bert_uncased_L-12_H-768_A-12-v1.0.1.model"

				self.entityPath=os.path.join(modelPath, entityName)
				if not Path(self.entityPath).is_file():
					print("downloading %s" % entityName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % entityName, self.entityPath)

				self.coref_model=os.path.join(modelPath, corefName)
				if not Path(self.coref_model).is_file():
					print("downloading %s" % corefName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % corefName, self.coref_model)

				self.quoteAttribModel=os.path.join(modelPath, quoteAttribName)
				if not Path(self.quoteAttribModel).is_file():
					print("downloading %s" % quoteAttribName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % quoteAttribName, self.quoteAttribModel)


			elif model_params["model"] == "small":
				entityName="entities_google_bert_uncased_L-4_H-256_A-4-v1.0.model"
				corefName="coref_google_bert_uncased_L-2_H-256_A-4-v1.0.model"
				quoteAttribName="speaker_google_bert_uncased_L-8_H-256_A-4-v1.0.1.model"

				self.entityPath=os.path.join(modelPath, entityName)
				if not Path(self.entityPath).is_file():
					print("downloading %s" % entityName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % entityName, self.entityPath)

				self.coref_model=os.path.join(modelPath, corefName)
				if not Path(self.coref_model).is_file():
					print("downloading %s" % corefName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % corefName, self.coref_model)

				self.quoteAttribModel=os.path.join(modelPath, quoteAttribName)
				if not Path(self.quoteAttribModel).is_file():
					print("downloading %s" % quoteAttribName)
					urllib.request.urlretrieve("http://people.ischool.berkeley.edu/~dbamman/booknlp_models/%s" % quoteAttribName, self.quoteAttribModel)

			elif model_params["model"] == "custom":
				self.entityPath=model_params["entity_model_path"]
				self.coref_model=model_params["coref_model_path"]
				self.quoteAttribModel=model_params["quote_attribution_model_path"]


			self.doEntities=self.doCoref=self.doQuoteAttrib=self.doSS=self.doEvent=False

			for pipe in pipes:
				if pipe not in valid_keys:
					print("unknown pipe: %s" % pipe)
					sys.exit(1)
				if pipe == "entity":
					self.doEntities=True
				elif pipe == "event":
					self.doEvent=True
				elif pipe == "coref":
					self.doCoref=True
				elif pipe == "supersense":
					self.doSS=True
				elif pipe == "quote":
					self.doQuoteAttrib=True

			tagsetPath="data/entity_cat.tagset"
			tagsetPath = pkg_resources.resource_filename(__name__, tagsetPath)


			if "referential_gender_hyperparameterFile" in model_params:
				self.gender_hyperparameterFile=model_params["referential_gender_hyperparameterFile"]
			else:
				self.gender_hyperparameterFile = pkg_resources.resource_filename(__name__, "data/gutenberg_prop_gender_terms.txt")
			
			pronominalCorefOnly=True

			if "pronominalCorefOnly" in model_params:
				pronominalCorefOnly=model_params["pronominalCorefOnly"]

			if not self.doEntities and self.doCoref:
				print("coref requires entity tagging")
				sys.exit(1)

			if not self.doQuoteAttrib and self.doCoref:
				print("coref requires quotation attribution")
				sys.exit(1)
			if not self.doEntities and self.doQuoteAttrib:
				print("quotation attribution requires entity tagging")
				sys.exit(1)	


			self.quoteTagger=QuoteTagger()

			if self.doEntities:
				self.entityTagger=LitBankEntityTagger(self.entityPath, tagsetPath)
				aliasPath = pkg_resources.resource_filename(__name__, "data/aliases.txt")
				self.name_resolver=NameCoref(aliasPath)


			if self.doQuoteAttrib:
				self.quote_attrib=QuotationAttribution(self.quoteAttribModel)

			
			if self.doCoref:
				self.litbank_coref=LitBankCoref(self.coref_model, self.gender_cats, pronominalCorefOnly=pronominalCorefOnly)

			self.tagger=SpacyPipeline(spacy_nlp)

			print("--- startup: %.3f seconds ---" % (time.time() - start_time))

	def get_syntax(self, tokens, entities, assignments, genders):

		def check_conj(tok, tokens):
			if tok.deprel == "conj" and tok.dephead != tok.token_id:
				# print("found conj", tok.text)
				return tokens[tok.dephead]
			return tok

		def get_head_in_range(start, end, tokens):
			for i in range(start, end+1):
				if tokens[i].dephead < start or tokens[i].dephead > end:
					return tokens[i]
			return None

		agents={}
		patients={}
		poss={}
		mods={}
		prop_mentions={}
		pron_mentions={}
		nom_mentions={}
		keys=Counter()


		toks_by_children={}
		for tok in tokens:
			if tok.dephead not in toks_by_children:
				toks_by_children[tok.dephead]={}
			toks_by_children[tok.dephead][tok]=1

		for idx, (start_token, end_token, cat, phrase) in enumerate(entities):
			ner_prop=cat.split("_")[0]
			ner_type=cat.split("_")[1]

			if ner_type != "PER":
				continue

			coref=assignments[idx]

			keys[coref]+=1
			if coref not in agents:
				agents[coref]=[]
				patients[coref]=[]
				poss[coref]=[]
				mods[coref]=[]
				prop_mentions[coref]=Counter()
				pron_mentions[coref]=Counter()
				nom_mentions[coref]=Counter()

			if ner_prop == "PROP":
				prop_mentions[coref][phrase]+=1
			elif ner_prop == "PRON":
				pron_mentions[coref][phrase]+=1
			elif ner_prop == "NOM":
				nom_mentions[coref][phrase]+=1


			tok=get_head_in_range(start_token, end_token, tokens)
			if tok is not None:

				tok=check_conj(tok, tokens)
				head=tokens[tok.dephead]

				# nsubj
				# mod
				if tok.deprel == "nsubj" and head.lemma == "be":
					for sibling in toks_by_children[head.token_id]:

						# "he was strong and happy", where happy -> conj -> strong -> attr/acomp -> be
						sibling_id=sibling.token_id
						sibling_tok=tokens[sibling_id]
						if (sibling_tok.deprel == "attr" or sibling_tok.deprel == "acomp") and (sibling_tok.pos == "NOUN" or sibling_tok.pos == "ADJ"):
							mods[coref].append({"w":sibling_tok.text, "i":sibling_tok.token_id})

							if sibling.token_id in toks_by_children:
								for grandsibling in toks_by_children[sibling.token_id]:
									grandsibling_id=grandsibling.token_id
									grandsibling_tok=tokens[grandsibling_id]

									if grandsibling_tok.deprel == "conj" and (grandsibling_tok.pos == "NOUN" or grandsibling_tok.pos == "ADJ"):
										mods[coref].append({"w":grandsibling_tok.text, "i":grandsibling_tok.token_id})



				# ("Bill and Ted ran" conj captured by check_conj above)
				elif tok.deprel == "nsubj" and head.pos == ("VERB"):
					agents[coref].append({"w":head.text, "i":head.token_id})

				# "Bill ducked and ran", where ran -> conj -> ducked
					for sibling in toks_by_children[head.token_id]:
						sibling_id=sibling.token_id
						sibling_tok=tokens[sibling_id]
						if sibling_tok.deprel == "conj" and sibling_tok.pos == "VERB":
							agents[coref].append({"w":sibling_tok.text, "i":sibling_tok.token_id})
				
				# "Jack was hit by John and William" conj captured by check_conj above
				elif tok.deprel == "pobj" and head.deprel == "agent":
					# not root
					if head.dephead != head.token_id:
						grandparent=tokens[head.dephead]
						if grandparent.pos.startswith("V"):
							agents[coref].append({"w":grandparent.text, "i":grandparent.token_id})


				# patient ("He loved Bill and Ted" conj captured by check_conj above)
				elif (tok.deprel == "dobj" or tok.deprel == "nsubjpass") and head.pos == "VERB":
					patients[coref].append({"w":head.text, "i":head.token_id})


				# poss

				elif tok.deprel == "poss":
					poss[coref].append({"w":head.text, "i":head.token_id})

					# "her house and car", where car -> conj -> house
					for sibling in toks_by_children[head.token_id]:
						sibling_id=sibling.token_id
						sibling_tok=tokens[sibling_id]
						if sibling_tok.deprel == "conj":
							poss[coref].append({"w":sibling_tok.text, "i":sibling_tok.token_id})
					

		data={}
		data["characters"]=[]

		for coref, total_count in keys.most_common():

			# must observe a character at least *twice*

			if total_count > 1:
				chardata={}
				chardata["agent"]=agents[coref]
				chardata["patient"]=patients[coref]
				chardata["mod"]=mods[coref]
				chardata["poss"]=poss[coref]
				chardata["id"]=coref
				if coref in genders:
					chardata["g"]=genders[coref]
				else:
					chardata["g"]=None
				chardata["count"]=total_count

				mentions={}

				pnames=[]
				for k,v in prop_mentions[coref].most_common():
					pnames.append({"c":v, "n":k})
				mentions["proper"]=pnames

				nnames=[]
				for k,v in nom_mentions[coref].most_common():
					nnames.append({"c":v, "n":k})
				mentions["common"]=nnames

				prnames=[]
				for k,v in pron_mentions[coref].most_common():
					prnames.append({"c":v, "n":k})
				mentions["pronoun"]=prnames

				chardata["mentions"]=mentions

				
				data["characters"].append(chardata)
			
		return data


	def normalize_character_name(self, name):
	    """
	    Normalize character name to camelCase format without spaces or special characters
	    """
	    import re
	    
	    # Remove special characters except spaces and apostrophes
	    name = re.sub(r"[^\w\s']", "", name)
	    
	    # Handle possessives (e.g., "Tom's" -> "Toms")
	    name = re.sub(r"'s\b", "s", name)
	    name = re.sub(r"'", "", name)
	    
	    # Split on whitespace and capitalize each word
	    words = name.split()
	    if not words:
	        return "UnknownCharacter"
	    
	    # First word capitalized, rest capitalized (camelCase)
	    normalized = words[0].capitalize()
	    for word in words[1:]:
	        normalized += word.capitalize()
	    
	    # Ensure it starts with a letter
	    if not normalized or not normalized[0].isalpha():
	        normalized = "character" + normalized.capitalize()
	    
	    return normalized

	def infer_age_category_with_scores(self, character_data):
	    """
	    Use semantic similarity to infer age category with confidence scores for all categories
	    """
	    try:
	        from sentence_transformers import SentenceTransformer
	        if not hasattr(self, '_age_model'):
	            self._age_model = SentenceTransformer('all-MiniLM-L6-v2')
	        model = self._age_model
	    except ImportError:
	        print("Warning: sentence-transformers not installed. Age inference unavailable.")
	        return {"category": "unknown", "scores": {"child": 0.0, "teen": 0.0, "adult": 0.0, "elder": 0.0}}
	    except Exception as e:
	        print(f"Warning: Could not load sentence transformer model: {e}")
	        return {"category": "unknown", "scores": {"child": 0.0, "teen": 0.0, "adult": 0.0, "elder": 0.0}}
	    
	    age_prototypes = {
	        'child': [
	            "young child", "little kid", "small child", "baby", "toddler", 
	            "young boy", "little girl", "infant", "youngster"
	        ],
	        'teen': [
	            "teenager", "adolescent", "young person", "teenage boy", 
	            "teenage girl", "youth", "high school student"
	        ],
	        'adult': [
	            "adult man", "adult woman", "grown person", "mature person",
	            "middle-aged man", "middle-aged woman", "working adult"
	        ],
	        'elder': [
	            "elderly person", "old man", "old woman", "senior citizen",
	            "aged person", "grandfather", "grandmother", "elderly gentleman"
	        ]
	    }
	    
	    # Get descriptors
	    descriptors = []
	    descriptors.extend([mod['w'] for mod in character_data.get('mod', [])])
	    descriptors.extend([mention['n'] for mention in character_data.get('mentions', {}).get('common', [])])
	    
	    if not descriptors:
	        return {"category": "unknown", "scores": {"child": 0.0, "teen": 0.0, "adult": 0.0, "elder": 0.0}}
	    
	    character_description = " ".join(descriptors)
	    
	    # Calculate similarities for ALL categories
	    category_scores = {}
	    best_category = "unknown"
	    best_score = 0.0
	    
	    try:
	        for category, prototypes in age_prototypes.items():
	            prototype_embeddings = model.encode(prototypes)
	            char_embedding = model.encode([character_description])
	            
	            similarities = model.similarity(char_embedding, prototype_embeddings)
	            max_similarity = float(similarities.max())
	            
	            category_scores[category] = round(max_similarity, 3)
	            
	            if max_similarity > best_score and max_similarity > 0.2:
	                best_score = max_similarity
	                best_category = category
	        
	    except Exception as e:
	        print(f"Warning: Error during age inference: {e}")
	        return {"category": "unknown", "scores": {"child": 0.0, "teen": 0.0, "adult": 0.0, "elder": 0.0}}
	    
	    return {"category": best_category, "scores": category_scores}

	def generate_character_json(self, entities, assignments, genders, chardata, outFolder, idd):
	    """
	    Generate a JSON file with character information including TTS settings and age inference with scores
	    """
	    
	    def map_gender_to_standard(gender_data):
	        """
	        Map gender inference results to 'male', 'female', or 'unknown' based on highest score
	        """
	        if gender_data is None:
	            return "unknown"
	            
	        # Get the inference scores
	        inference_scores = gender_data.get("inference", {})
	        
	        # Map pronoun groups to standard genders
	        gender_mapping = {
	            "he/him/his": "male",
	            "she/her": "female",
	            # Ignore other categories like "they/them/their", "xe/xem/xyr", etc.
	        }
	        
	        # Find the highest scoring valid gender
	        max_score = 0.0
	        best_gender = "unknown"
	        
	        for pronoun_group, score in inference_scores.items():
	            if pronoun_group in gender_mapping and score > max_score:
	                max_score = score
	                best_gender = gender_mapping[pronoun_group]
	        
	        # Only return a gender if the confidence is reasonable (e.g., > 0.1)
	        if max_score > 0.1:
	            return best_gender
	        else:
	            return "unknown"
	    
	    # Get canonical names for characters
	    names = {}
	    for idx, (start, end, cat, text) in enumerate(entities):
	        coref = assignments[idx]
	        if coref not in names:
	            names[coref] = Counter()
	        ner_prop = cat.split("_")[0]
	        ner_type = cat.split("_")[1]
	        if ner_prop == "PROP":
	            names[coref][text.lower()] += 10
	        elif ner_prop == "NOM":
	            names[coref][text.lower()] += 1
	        else:
	            names[coref][text.lower()] += 0.001
	    
	    # Get canonical name for each character ID
	    char_names = {}
	    for coref, name_counter in names.items():
	        if name_counter:
	            char_names[coref] = name_counter.most_common(1)[0][0]
	        else:
	            char_names[coref] = f"character_{coref}"
	    
	    # Build character information
	    characters_info = []
	    
	    # Add narrator first
	    narrator_char = {
	        "character_id": "Narrator",
	        "canonical_name": "Narrator",
	        "normalized_name": "Narrator",
	        "inferred_gender": "unknown",
	        "gender_scores": {},
	        "inferred_age_category": "unknown",
	        "age_confidence_scores": {"child": 0.0, "teen": 0.0, "adult": 0.0, "elder": 0.0},
	        "mention_count": 0,
	        "tts_engine": "XTTSv2",
	        "language": "eng",
	        "voice": None
	    }
	    characters_info.append(narrator_char)
	    
	    # Add characters from chardata
	    for character in chardata["characters"]:
	        char_id = character["id"]
	        age_result = self.infer_age_category_with_scores(character)
	        canonical_name = char_names.get(char_id, f"character_{char_id}")
	        
	        # Map the gender to standard format
	        raw_gender_data = character.get("g", None)
	        standardized_gender = map_gender_to_standard(raw_gender_data)
	        
	        # Preserve the original gender scores
	        gender_scores = {}
	        if raw_gender_data and "inference" in raw_gender_data:
	            gender_scores = raw_gender_data["inference"]
	        
	        char_info = {
	            "character_id": char_id,
	            "canonical_name": canonical_name,
	            "normalized_name": self.normalize_character_name(canonical_name),
	            "inferred_gender": standardized_gender,
	            "gender_scores": gender_scores,
	            "inferred_age_category": age_result["category"],
	            "age_confidence_scores": age_result["scores"],
	            "mention_count": character["count"],
	            "tts_engine": "XTTSv2",
	            "language": "eng",
	            "voice": None
	        }
	        characters_info.append(char_info)
	    
	    # Build the JSON structure
	    result = {
	        "metadata": {
	            "generated_by": "BookNLP",
	            "generated_at": "2025-07-18 05:43:37",
	            "generated_by_user": "DrewThomasson",
	            "document_id": idd,
	            "total_characters": len(characters_info)
	        },
	        "characters": characters_info
	    }
	    
	    # Write JSON file
	    with open(join(outFolder, "%s.characters.json" % (idd)), "w", encoding="utf-8") as out:
	        json.dump(result, out, indent=2, ensure_ascii=False)
	    
	    return result


	def generate_simplified_character_json(self, entities, assignments, genders, chardata, outFolder, idd):
	    """
	    Generate a simplified JSON file with only essential character information for TTS
	    """
	    
	    def map_gender_to_standard(gender_data):
	        """
	        Map gender inference results to 'male', 'female', or 'unknown' based on highest score
	        """
	        if gender_data is None:
	            return "unknown"
	            
	        # Get the inference scores
	        inference_scores = gender_data.get("inference", {})
	        
	        # Map pronoun groups to standard genders
	        gender_mapping = {
	            "he/him/his": "male",
	            "she/her": "female",
	            # Ignore other categories like "they/them/their", "xe/xem/xyr", etc.
	        }
	        
	        # Find the highest scoring valid gender
	        max_score = 0.0
	        best_gender = "unknown"
	        
	        for pronoun_group, score in inference_scores.items():
	            if pronoun_group in gender_mapping and score > max_score:
	                max_score = score
	                best_gender = gender_mapping[pronoun_group]
	        
	        # Only return a gender if the confidence is reasonable (e.g., > 0.1)
	        if max_score > 0.1:
	            return best_gender
	        else:
	            return "unknown"
	    
	    # Get canonical names for characters
	    names = {}
	    for idx, (start, end, cat, text) in enumerate(entities):
	        coref = assignments[idx]
	        if coref not in names:
	            names[coref] = Counter()
	        ner_prop = cat.split("_")[0]
	        ner_type = cat.split("_")[1]
	        if ner_prop == "PROP":
	            names[coref][text.lower()] += 10
	        elif ner_prop == "NOM":
	            names[coref][text.lower()] += 1
	        else:
	            names[coref][text.lower()] += 0.001
	    
	    # Get canonical name for each character ID
	    char_names = {}
	    for coref, name_counter in names.items():
	        if name_counter:
	            char_names[coref] = name_counter.most_common(1)[0][0]
	        else:
	            char_names[coref] = f"character_{coref}"
	    
	    # Build simplified character information
	    characters_info = []
	    
	    # Add narrator first
	    narrator_char = {
	        "normalized_name": "Narrator",
	        "inferred_gender": "unknown",
	        "inferred_age_category": "unknown",
	        "tts_engine": "XTTSv2",
	        "language": "eng",
	        "voice": None
	    }
	    characters_info.append(narrator_char)
	    
	    # Add characters from chardata
	    for character in chardata["characters"]:
	        char_id = character["id"]
	        age_result = self.infer_age_category_with_scores(character)
	        canonical_name = char_names.get(char_id, f"character_{char_id}")
	        
	        # Map the gender to standard format
	        raw_gender_data = character.get("g", None)
	        standardized_gender = map_gender_to_standard(raw_gender_data)
	        
	        char_info = {
	            "normalized_name": self.normalize_character_name(canonical_name),
	            "inferred_gender": standardized_gender,
	            "inferred_age_category": age_result["category"],
	            "tts_engine": "XTTSv2",
	            "language": "eng",
	            "voice": None
	        }
	        characters_info.append(char_info)
	    
	    # Build the simplified JSON structure
	    result = {
	        "characters": characters_info
	    }
	    
	    # Write simplified JSON file
	    with open(join(outFolder, "%s.characters_simple.json" % (idd)), "w", encoding="utf-8") as out:
	        json.dump(result, out, indent=2, ensure_ascii=False)
	    
	    return result

	    
	def fix_punctuation_spacing(self, text):
	    """
	    Fix spacing around punctuation marks to follow standard English conventions
	    """
	    import re
	    
	    # First pass - fix quotes more aggressively
	    # Remove ALL spaces immediately after opening quotes
	    text = re.sub(r'"\s+', '"', text)
	    text = re.sub(r"'\s+", "'", text)
	    
	    # Remove ALL spaces immediately before closing quotes
	    text = re.sub(r'\s+"', '"', text)
	    text = re.sub(r"\s+'", "'", text)
	    
	    # Remove spaces before common punctuation marks
	    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
	    
	    # Remove spaces before closing quotes, parentheses, brackets
	    text = re.sub(r'\s+(["\'\)\]\}])', r'\1', text)
	    
	    # Fix contractions - remove spaces around apostrophes in contractions
	    text = re.sub(r'\s+\'\s*(\w+)', r"'\1", text)
	    text = re.sub(r'(\w+)\s+\'\s*(\w+)', r"\1'\2", text)
	    
	    # Handle possessives - remove space before 's
	    text = re.sub(r'(\w+)\s+\'\s*s\b', r"\1's", text)
	    
	    # Add space after punctuation if missing (but not before closing punctuation)
	    text = re.sub(r'([,.!?;:])([^\s"\'\)\]\}\n])', r'\1 \2', text)
	    
	    # Handle opening parentheses, brackets - remove space after
	    text = re.sub(r'([\(\[\{])\s+', r'\1', text)
	    
	    # Fix underscores (italics) - remove spaces around them but add space after closing underscore
	    text = re.sub(r'_(\w+)_(\w)', r'_\1_ \2', text)
	    
	    # Fix double spaces
	    text = re.sub(r'\s{2,}', ' ', text)
	    
	    return text.strip()

	def generate_book_with_character_tags(self, tokens, quotes, attributed_quotations, entities, assignments, genders, chardata, outFolder, idd):
	    """
	    Generate a .book.txt file with character name tags surrounding each sentence
	    """
	    
	    # Get canonical names for characters
	    names = {}
	    for idx, (start, end, cat, text) in enumerate(entities):
	        coref = assignments[idx]
	        if coref not in names:
	            names[coref] = Counter()
	        ner_prop = cat.split("_")[0]
	        ner_type = cat.split("_")[1]
	        if ner_prop == "PROP":
	            names[coref][text.lower()] += 10
	        elif ner_prop == "NOM":
	            names[coref][text.lower()] += 1
	        else:
	            names[coref][text.lower()] += 0.001
	    
	    # Get canonical name for each character ID and create normalized versions
	    char_names = {}
	    normalized_char_names = {}
	    for coref, name_counter in names.items():
	        if name_counter:
	            canonical_name = name_counter.most_common(1)[0][0].title()
	            char_names[coref] = canonical_name
	            normalized_char_names[coref] = self.normalize_character_name(canonical_name)
	        else:
	            char_names[coref] = f"Character{coref}"
	            normalized_char_names[coref] = f"character{coref}"
	    
	    # Add narrator to mappings
	    char_names["Narrator"] = "Narrator"
	    normalized_char_names["Narrator"] = "Narrator"
	    
	    # Create mapping of token ranges to quotes and speakers
	    quote_ranges = {}
	    for idx, (start, end) in enumerate(quotes):
	        mention_id = attributed_quotations[idx]
	        if mention_id is not None:
	            speaker_id = assignments[mention_id]
	        else:
	            speaker_id = "Narrator"
	        
	        for token_idx in range(start, end + 1):
	            quote_ranges[token_idx] = speaker_id
	    
	    # Group tokens by sentence
	    sentences = {}
	    for token in tokens:
	        sent_id = token.sentence_id
	        if sent_id not in sentences:
	            sentences[sent_id] = []
	        sentences[sent_id].append(token)
	    
	    # Build the tagged text
	    result_lines = []
	    
	    for sent_id in sorted(sentences.keys()):
	        sent_tokens = sentences[sent_id]
	        sent_text = " ".join([token.text for token in sent_tokens])
	        
	        # Fix punctuation spacing
	        sent_text = self.fix_punctuation_spacing(sent_text)
	        
	        # Determine speaker for this sentence
	        # Check if any tokens in this sentence are part of quotes
	        speaker_ids_in_sentence = set()
	        
	        for token in sent_tokens:
	            if token.token_id in quote_ranges:
	                speaker_ids_in_sentence.add(quote_ranges[token.token_id])
	        
	        # If exactly one speaker, use that speaker; otherwise default to narrator
	        if len(speaker_ids_in_sentence) == 1:
	            speaker_id = list(speaker_ids_in_sentence)[0]
	        else:
	            speaker_id = "Narrator"
	        
	        # Get the normalized name for the speaker (used in tags)
	        speaker_name = normalized_char_names.get(speaker_id, f"character{speaker_id}")
	        
	        # Format the sentence with character name tags using normalized names
	        tagged_sentence = f"[{speaker_name}] {sent_text} [/]"
	        result_lines.append(tagged_sentence)
	    
	    # Write the tagged text file
	    with open(join(outFolder, "%s.book.txt" % (idd)), "w", encoding="utf-8") as out:
	        out.write("\n".join(result_lines))
	    
	    return result_lines



	def process(self, filename, outFolder, idd):		

		with torch.no_grad():

			start_time = time.time()
			originalTime=start_time

			with open(filename, encoding='utf-8') as file:
				data=file.read()

				if len(data) == 0:
					print("Input file is empty: %s" % filename)
					return 

				try:
					os.makedirs(outFolder)
				except FileExistsError:
					pass

					
				tokens=self.tagger.tag(data)
				
				print("--- spacy: %.3f seconds ---" % (time.time() - start_time))
				start_time=time.time()

				if self.doEvent or self.doEntities or self.doSS:

					entity_vals=self.entityTagger.tag(tokens, doEvent=self.doEvent, doEntities=self.doEntities, doSS=self.doSS)
					entity_vals["entities"]=sorted(entity_vals["entities"])
					if self.doSS:
						supersense_entities=entity_vals["supersense"]
						with open(join(outFolder, "%s.supersense" % (idd)), "w", encoding="utf-8") as out:
							out.write("start_token\tend_token\tsupersense_category\ttext\n")
							for start, end, cat, text in supersense_entities:
								out.write("%s\t%s\t%s\t%s\n" % (start, end, cat, text))

					if self.doEvent:
						events=entity_vals["events"]
						for token in tokens:
							if token.token_id in events:
								token.event="EVENT"

					with open(join(outFolder, "%s.tokens" % (idd)), "w", encoding="utf-8") as out:
						out.write("%s\n" % '\t'.join(["paragraph_ID", "sentence_ID", "token_ID_within_sentence", "token_ID_within_document", "word", "lemma", "byte_onset", "byte_offset", "POS_tag", "fine_POS_tag", "dependency_relation", "syntactic_head_ID", "event"]))
						for token in tokens:
							out.write("%s\n" % token)

					print("--- entities: %.3f seconds ---" % (time.time() - start_time))
					start_time=time.time()

				in_quotes=[]
				quotes=self.quoteTagger.tag(tokens)

				print("--- quotes: %.3f seconds ---" % (time.time() - start_time))
				start_time=time.time()

				if self.doQuoteAttrib:

					entities=entity_vals["entities"]
					attributed_quotations=self.quote_attrib.tag(quotes, entities, tokens)

					print("--- attribution: %.3f seconds ---" % (time.time() - start_time))
					# return time.time() - start_time
					start_time=time.time()

				if self.doEntities:

					entities=entity_vals["entities"]
		
					in_quotes=[]

					for start, end, cat, text in entities:
	
						if tokens[start].inQuote or tokens[end].inQuote:
							in_quotes.append(1)
						else:
							in_quotes.append(0)


					# Create entity for first-person narrator, if present
					refs=self.name_resolver.cluster_narrator(entities, in_quotes, tokens)
				
					# Cluster non-PER PROP mentions that are identical
					refs=self.name_resolver.cluster_identical_propers(entities, refs)

					# Cluster mentions of named people
					refs=self.name_resolver.cluster_only_nouns(entities, refs, tokens)

					print("--- name coref: %.3f seconds ---" % (time.time() - start_time))

					start_time=time.time()

					# Infer referential gender from he/she/they mentions around characters
					
					genderEM=GenderEM(tokens=tokens, entities=entities, refs=refs, genders=self.gender_cats, hyperparameterFile=self.gender_hyperparameterFile)
					genders=genderEM.tag(entities, tokens, refs)
				
				assignments=None
				if self.doEntities:
					assignments=copy.deepcopy(refs)

				if self.doCoref:
					torch.cuda.empty_cache()
					assignments=self.litbank_coref.tag(tokens, entities, refs, genders, attributed_quotations, quotes)

					print("--- coref: %.3f seconds ---" % (time.time() - start_time))
					start_time=time.time()

					ent_names={}
					for a, e in zip(assignments, entities):
						if a not in ent_names:
							ent_names[a]=Counter()
						ent_names[a][e[3]]+=1
				
					# Update gender estimates from coref data
					genders=genderEM.update_gender_from_coref(genders, entities, assignments)

					chardata=self.get_syntax(tokens, entities, assignments, genders)
					with open(join(outFolder, "%s.book" % (idd)), "w", encoding="utf-8") as out:
						json.dump(chardata, out)

				if self.doEntities:
					# Write entities and coref			
					with open(join(outFolder, "%s.entities" % (idd)), "w", encoding="utf-8") as out:
						out.write("COREF\tstart_token\tend_token\tprop\tcat\ttext\n")
						for idx, assignment in enumerate(assignments):
							start, end, cat, text=entities[idx]
							ner_prop=cat.split("_")[0]
							ner_type=cat.split("_")[1]
							out.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (assignment, start, end, ner_prop, ner_type, text))


				if self.doQuoteAttrib:
					with open(join(outFolder, "%s.quotes" % (idd)), "w", encoding="utf-8") as out:
						out.write('\t'.join(["quote_start", "quote_end", "mention_start", "mention_end", "mention_phrase", "char_id", "quote"]) + "\n")

						for idx, line in enumerate(attributed_quotations):
							q_start, q_end=quotes[idx]
							mention=attributed_quotations[idx]
							if mention is not None:
								entity=entities[mention]
								speaker_id=assignments[mention]
								e_start=entity[0]
								e_end=entity[1]
								cat=entity[3]
								speak=speaker_id
							else:
								e_start=None
								e_end=None
								cat=None
								speak=None
							quote=[tok.text for tok in tokens[q_start:q_end+1]]
							out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (q_start, q_end, e_start, e_end, cat, speak, ' '.join(quote)))
					
						out.close()

				if self.doQuoteAttrib and self.doCoref:

					# get canonical name for character
					names={}
					for idx, (start, end, cat, text) in enumerate(entities):
						coref=assignments[idx]
						if coref not in names:
							names[coref]=Counter()
						ner_prop=cat.split("_")[0]
						ner_type=cat.split("_")[1]
						if ner_prop == "PROP":
							names[coref][text.lower()]+=10
						elif ner_prop == "NOM":
							names[coref][text.lower()]+=1
						else:
							names[coref][text.lower()]+=.001

					# Generate character info JSON
					print("--- generating character JSON: start ---")
					char_start_time = time.time()
					self.generate_character_json(entities, assignments, genders, chardata, outFolder, idd)
					print("--- character JSON: %.3f seconds ---" % (time.time() - char_start_time))

					# Generate simplified character info JSON
					print("--- generating simplified character JSON: start ---")
					simple_char_start_time = time.time()
					self.generate_simplified_character_json(entities, assignments, genders, chardata, outFolder, idd)
					print("--- simplified character JSON: %.3f seconds ---" % (time.time() - simple_char_start_time))

					# Generate book with character tags
					print("--- generating tagged book: start ---")
					book_start_time = time.time()
					self.generate_book_with_character_tags(tokens, quotes, attributed_quotations, 
					                                      entities, assignments, genders, chardata, 
					                                      outFolder, idd)
					print("--- tagged book: %.3f seconds ---" % (time.time() - book_start_time))

					with open(join(outFolder, "%s.book.html" % (idd)), "w", encoding="utf-8") as out:
						out.write("<html>")
						out.write("""<head>
		  <meta charset="UTF-8">
		</head>""")
						out.write("<h2>Named characters</h2>\n")
						for character in chardata["characters"]:
							char_id=character["id"]

							proper_names=character["mentions"]["proper"]
							if len(proper_names) > 0 or char_id == 0: # 0=narrator
								proper_name_list="/".join(["%s (%s)" % (name["n"], name["c"]) for name in proper_names])

								common_names=character["mentions"]["common"]
								common_name_list="/".join(["%s (%s)" % (name["n"], name["c"]) for name in common_names])

								char_count=character["count"]

								if char_id == 0:
									if len(proper_name_list) == 0:
										proper_name_list="[NARRATOR]"
									else:
										proper_name_list+="/[NARRATOR]"
								out.write("%s %s %s <br />\n" % (char_count, proper_name_list, common_name_list))

				
						out.write("<p>\n")

						out.write("<h2>Major entities (proper, common)</h2>")

						major_places={}
						for prop in ["PROP", "NOM"]:
							major_places[prop]={}
							for cat in ["FAC", "GPE", "LOC", "PER", "ORG", "VEH"]:
								major_places[prop][cat]={}

						for idx, (start, end, cat, text) in enumerate(entities):
							coref=assignments[idx]
			
							ner_prop=cat.split("_")[0]
							ner_type=cat.split("_")[1]
							if ner_prop != "PRON":
								if coref not in major_places[ner_prop][ner_type]:
									major_places[ner_prop][ner_type][coref]=Counter()
								major_places[ner_prop][ner_type][coref][text]+=1

						max_entities_to_display=10
						for cat in ["FAC", "GPE", "LOC", "PER", "ORG", "VEH"]:
							out.write("<h3>%s</h3>" % cat)
							for prop in ["PROP", "NOM"]:
								freqs={}
								for coref in major_places[prop][cat]:
									freqs[coref]=sum(major_places[prop][cat][coref].values())

								sorted_freqs=sorted(freqs.items(), key=lambda x: x[1], reverse=True)
								for k,v in sorted_freqs[:max_entities_to_display]:
									ent_names=[]
									for name, count in major_places[prop][cat][k].most_common():
										ent_names.append("%s" % (name))
									out.write("%s %s <br />"% (v, '/'.join(ent_names)))
								out.write("<p>")



						out.write("<h2>Text</h2>\n")
						

						beforeToks=[""]*len(tokens)
						afterToks=[""]*len(tokens)

						lastP=None

						for idx, (start, end, cat, text) in enumerate(entities):
							coref=assignments[idx]
							name=names[coref].most_common(1)[0][0]
							beforeToks[start]+="<font color=\"#D0D0D0\">[</font>"
							afterToks[end]="<font color=\"#D0D0D0\">]</font><font color=\"#FF00FF\"><sub>%s-%s</sub></font>" % (coref, name) + afterToks[end]

						for idx, (start, end) in enumerate(quotes):
							mention_id=attributed_quotations[idx]
							if mention_id is not None:
								speaker_id=assignments[mention_id]
								name=names[speaker_id].most_common(1)[0][0]
							else:
								speaker_id="None"
								name="None"
							beforeToks[start]+="<font color=\"#666699\">"
							afterToks[end]+="</font><sub>[%s-%s]</sub>" % (speaker_id, name)

						for idx in range(len(tokens)):
							if tokens[idx].paragraph_id != lastP:
								out.write("<p />")
							out.write("%s%s%s " % (beforeToks[idx], escape(tokens[idx].text), afterToks[idx])) 
							lastP=tokens[idx].paragraph_id	

						
						out.write("</html>")

				print("--- TOTAL (excl. startup): %.3f seconds ---, %s words" % (time.time() - originalTime, len(tokens)))
				return time.time() - originalTime