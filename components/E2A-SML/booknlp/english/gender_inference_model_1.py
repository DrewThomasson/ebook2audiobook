
"""
Code for inferring the referential gender of name-clustered characters (e.g., ELIZABETH BENNETT = {Elizabeth, Lizzy, Elizabeth Bennett}) and common NPs (e.g "the boy") solely from the gendered pronouns (he/his/him/she/her/they/them/ze/xe/etc.) that appear near them. This method uses the IBM model 1 EM alignment algorithm (originally used for MT) to align entities with pronoun tokens, starting from a prior that all entities are gender-neutral and then updating that belief based on their explanatory power for the pronouns that surround them.

This method encodes several assumptions:

* This method describes the referential gender of characters, and not their gender identity. Characters are described by the pronouns used to refer to them (e.g., he/him, she/her) rather than labels like "M/F".

* Prior information on the alignment of names with referential gender (e.g., from government records or larger background datasets) can be used to provide some information to inform this process if desired (e.g., "Tom" is often associated with he/him in pre-1923 English texts), but should be updateable *in the context of a specific book* (e.g., "Tom" in the book "Tom and Some Other Girls", where Tom is aligned with she/her). 

* Users should be free to define the referential gender categories used here.  The default is {he, him, his}, 
{she, her} and {they, them, their}, but can be expanded to include categories such as {xe, xem, xyr, xir}, {ze, zem, zir, hir}, etc.


"""


# requires scipy==1.5.4
from collections import Counter
import sys
from tqdm import tqdm
from os import listdir
from os.path import isfile
import os
from booknlp.common.pipelines import Token

import random

class GenderEM:

	def __init__(self, outfile=None, tokens=None, entities=None, entityFiles=None, tokenFiles=None, hyperparameterFile=None, distance=25, num_epochs=25, refs=None, upper=10, use_tagged_pronouns_only=True, genders=[["he", "him", "his"],["she", "her"],	["they", "them", "their"]] ):

		# Number of epochs for EM
		self.num_epochs=num_epochs

		# Candidates entities must within this number of preceding tokens of pronouns
		self.distance=distance

		# maximum pseudocount value (set lower to contrain how much influence priors have)
		self.upper=upper

		self.honorifics={"mr.":1, "mrs.":1, "miss":1, "lady":1, "sir":1, "captain":1, "mr":1, "lord":1, "aunt":1, "madame":1, "mrs":1, "uncle":1, "colonel":1, "monsieur":1, "mademoiselle":1, "general":1, "major":1, "sergeant":1, "ms.":1,  "king":1, "queen":1, "herr":1, "frau":1, "fräulein":1, "dame":1, "mister":1, "master":1, "mistress":1, "prince":1, "princess":1, "lieutenant":1 }
		self.honorific_priors={}
		self.use_tagged_pronouns_only=use_tagged_pronouns_only
		self.genders=genders

		self.genderID={}
		self.gender_pronouns={}

		self.num_genders=len(self.genders)

		for idx, gender in enumerate(self.genders):
			self.genderID["/".join(gender)]=idx
			for term in gender:
				self.gender_pronouns[term]=idx

		self.reverseID={self.genderID[k]:k for k in self.genderID}
		

		# f = he/she/they
		# e = John, Kate, the man, her husband, his mother

		self.joint_e_f_counts={}
		self.e_counts={}

		self.t_f_e={}

		self.hyperparameters={}

		if hyperparameterFile is not None:
			self.read_hyperparams(hyperparameterFile)

		self.vocab={}

		if entityFiles is not None and tokenFiles is not None: 
			self.build_vocab_from_files(entityFiles, tokenFiles)
		elif tokens is not None and entities is not None and refs is not None:
			self.build_vocab(tokens, entities, refs)


		self.add_hyperparameters_to_counts(refs=refs, entities=entities, tokens=tokens)

		self.maximization()
		self.delete_counts()

		self.outfile=outfile


	def add_hyperparameters_to_counts(self, refs=None, entities=None, tokens=None):
		for e in self.vocab:

			mf=[1]*self.num_genders

			# add pseudocounts if we have them from the hyperparameters
			if self.hyperparameters is not None and e in self.hyperparameters:
				mf=self.hyperparameters[e]

			for f in range(self.num_genders):
				self.joint_e_f_counts[e,f]=mf[f] + 0.1
				if e not in self.e_counts:
					self.e_counts[e]=0
				self.e_counts[e]+=mf[f] + 0.1
		

		# for entities/coref IDs, update the coref ID to include priors on the names associated with that ID
		# e.g. 17 -> Jane Bennett, Jane, etc. -- we want to include our priors on "Jane" within entity 17

		counts={}
		if refs is not None:
			for idx, ref in enumerate(refs):
				start, end, cat, text=entities[idx]

				prop=cat.split("_")[0]
				cat=cat.split("_")[1]

				phraseHead=None

				if prop == "NOM":
					phraseHead=self.get_head(start, end, tokens)

				if phraseHead is not None:
					key="%s\t%s" % (tokens[phraseHead].text, prop)
				else:
					key="%s\t%s" % (text, prop)

				if ref != -1:
					if ref not in counts:
						counts[ref]=Counter()
					counts[ref][key.lower()]+=1

		for e in self.vocab:
			mf=[0.]*self.num_genders
			parts=e.split("\t")
			if parts[1].lower() == "coref":
				idd=int(parts[0])

				if idd != -1:

					for text in counts[idd]:

						# add prior over entire name if present (e.g., "[Tom]")
						for f in range(self.num_genders):
							if (text,f) in self.joint_e_f_counts:
								mf[f]=self.joint_e_f_counts[text,f] * counts[idd][text]

					if sum(mf) > self.upper:
						for i in range(self.num_genders):
							mf[i]=(mf[i]/sum(mf)) * self.upper

					for text in counts[idd]:

						# add prior over honorifics if present (e.g., "[mr.] sawyer")
						first_name_token=text.split(" ")[0]
						if first_name_token in self.honorific_priors:
							for f in range(self.num_genders):
								mf[f]=self.honorific_priors[first_name_token][f] * counts[idd][text] * 10000


					self.e_counts[e]=0
					for f in range(self.num_genders):
						self.joint_e_f_counts[e,f]=mf[f] + 0.1
						self.e_counts[e]+=mf[f] + 0.1

	def read_hyperparams(self, filename):
		self.hyperparameters={}
		with open(filename, encoding='utf-8') as file:
			header=file.readline().rstrip()
			gender_mapping={}
			for idx, val in enumerate(header.split("\t")[2:]):
				if val in self.genderID:
					gender_mapping[self.genderID[val]]=idx+2

				else:
					print("NOTE PRIOR CATEGORY %s NOT AMONG GENDERS" % val)

			for line in file:
				cols=line.rstrip().split("\t")
				term=cols[0]
				proper=cols[1]

				vals=[0]*(self.num_genders)
				for val in gender_mapping:
					vals[val]=float(cols[gender_mapping[val]])

				first_token=term.split(" ")[0]
				if first_token in self.honorifics:
					if first_token not in self.honorific_priors:
						self.honorific_priors[first_token]=[0]*self.num_genders

					for i in range(self.num_genders):
						self.honorific_priors[first_token][i]+=vals[i]

				total=sum(vals)
				if total >= self.upper:
					for i in range(len(vals)):
						vals[i]=(vals[i]/total) * self.upper
					
					self.hyperparameters[("%s\t%s" % (term, proper)).lower()]=vals

			for honorific in self.honorific_priors:
				total=sum(self.honorific_priors[honorific])
				if total >= self.upper:
					for i in range(self.num_genders):
						self.honorific_priors[honorific][i]=(self.honorific_priors[honorific][i]/total) * self.upper
					
	def get_head(self, start, end, tokens):
		phraseHead=None
		for idd in range(start, end+1):
			head=tokens[idd].dephead
			if head < start or head > end:
				phraseHead=idd
		return phraseHead

	def build_vocab(self, tokens, entities, refs=None):


		for term in self.hyperparameters:
			self.vocab[term]=1

		for idx, (start, end, cat, text) in enumerate(entities):

			prop=cat.split("_")[0]
			cat=cat.split("_")[1]

			if cat == "PER":

				if refs is not None and refs[idx] != -1:
					key="%s\t%s" % (refs[idx], "COREF")

				else:

					phraseHead=None

					if prop == "NOM":
						phraseHead=self.get_head(start, end, tokens)

					if phraseHead is not None:
						key="%s\t%s" % (tokens[phraseHead].text, prop)
					else:
						key="%s\t%s" % (text, prop)


				self.vocab[key.lower()]=1					


	def build_vocab_from_files(self, entityFiles, tokenFiles):
	

		for term in self.hyperparameters:
			self.vocab[term]=1

		for idx in tqdm(range(len(entityFiles))):

			entities=self.read_entities(entityFiles[idx])
			tokens=self.read_tokens(tokenFiles[idx])

			self.build_vocab(tokens, entities)



	def tagFromFile(self, entityFiles, tokenFiles):
		
		all_X=[]
		all_Y=[]

		for idx in tqdm(range(len(entityFiles))):

			entities=self.read_entities(entityFiles[idx])
			tokens=self.read_tokens(tokenFiles[idx])

			X, Y=self.process(tokens, entities)
			all_X.append(X)
			all_Y.append(Y)


		for epoch in range(self.num_epochs):
			
			for i in tqdm(range(len(all_X))):
				for e, f in zip(all_X[i], all_Y[i]):
					self.update(e,f)

			self.maximization()
			self.print(epoch)
			self.delete_counts()
			self.add_hyperparameters_to_counts()


	def tag(self, entities, tokens, refs, minThreshold=0):

		X, Y=self.process(tokens, entities, refs)	

		for epoch in range(self.num_epochs):
			
			for e, f in zip(X, Y):
				self.update(e,f)

			self.maximization()
			if epoch < self.num_epochs-1:
				self.delete_counts()
				self.add_hyperparameters_to_counts(refs=refs, entities=entities, tokens=tokens)


		genders={}
		for e, f in self.t_f_e:
			if f == 1:

				vals={}
				total=0
				for i in range(self.num_genders):
					vals[self.reverseID[i]] = self.joint_e_f_counts[e,i]
					total+=vals[self.reverseID[i]]

				if total > 0:
					for val in vals:
						vals[val]=float("%.3f" % (vals[val]/total))

				maxID=None
				maxVal=0
				for val in vals:
					if vals[val] > maxVal:
						maxVal=vals[val]
						maxID=val

				cat=e.split("\t")[1]
				if cat == "coref":
					idd=int(e.split("\t")[0])
					genders[idd]={"inference":vals, "argmax":maxID, "max":maxVal, "total":float("%.3f" % total)}

		return genders

	def print(self, epoch):
		with open("%s.%s" % (self.outfile, epoch), "w", encoding="utf-8") as out:
			valstr=[]
			for gender in self.genders:
				valstr.append('/'.join(gender))

			out.write("%s\t%s\t%s\n" % ("term", "proper", '\t'.join(valstr)))

			for e, f in self.t_f_e:
				if f == 1:
					vals=[0]*self.num_genders
					for i in range(self.num_genders):
						vals[i] = self.joint_e_f_counts[e,i]

					out.write("%s\t%s\n" % (e, '\t'.join(["%.3f" % x for x in vals])))


	# get all entities in a window *before* a target pronoun
	def get_mentions(self, loc_starts, idx):

		mentions=[]

		for i in range(1,self.distance):
			j=idx-i
			if j in loc_starts:
				for end, comp, text in loc_starts[j]:
					# skip entities that enclose the pronoun 
					if end < idx:
						mentions.append((j, end, comp, text))

		return mentions


	def update(self, e_seq, f_seq):

		for i, f in enumerate(f_seq):
			total=0
			for j, e in enumerate(e_seq):
				total+=self.t_f_e[e, f]
			for j, e in enumerate(e_seq):
				delta_k_i_j=self.t_f_e[e, f] / total

				self.joint_e_f_counts[e,f]+=delta_k_i_j
				self.e_counts[e]+=delta_k_i_j


	def maximization(self, delete_counts=True):

		for (e,f) in self.joint_e_f_counts:

			if self.e_counts[e] > 0:
				self.t_f_e[e,f]=self.joint_e_f_counts[e,f]/self.e_counts[e]
			else:
				self.t_f_e[e,f]=0

			parts=e.split("\t")

	def delete_counts(self):
		for (e,f) in self.joint_e_f_counts:
			self.joint_e_f_counts[e,f]=0
		
		for e in self.e_counts:
			self.e_counts[e]=0


	def process(self, toks, entities, refs=None):

		# organize the token start positions for each entity so we can find them faster
		loc_starts={}

		tagged_pronouns=[]

		for idx, (start, end, cat, text) in enumerate(entities):
			prop=cat.split("_")[0]
			ner_type=cat.split("_")[1]

			if ner_type == "PER":

				if text.lower() in self.gender_pronouns:
					tagged_pronouns.append(start)

				# if this mention is already coreferent (e.g., through name clustering), use that coref ID instead
				if refs is not None and refs[idx] != -1:
					key="%s\t%s" % (refs[idx], "COREF")

				else:
					phraseHead=None

					if prop == "NOM":
						phraseHead=self.get_head(start, end, toks)

					if phraseHead is not None:
						key="%s\t%s" % (toks[phraseHead].text, prop)
					else:
						key="%s\t%s" % (text, prop)


				if start not in loc_starts:
					loc_starts[start]=[]

				loc_starts[start].append((end, idx, key))

		X=[]
		Y=[]

		# for each gendered pronoun in the text, identify all entity/common NP mentions in a window around it
		if self.use_tagged_pronouns_only:
			for idx in tagged_pronouns:
				tok=toks[idx].text
				mentions=self.get_mentions(loc_starts, idx)
				mention_refs=[]
				for start, end, loc_idx, text in mentions:
					mention_refs.append(text.lower())

				if len(mention_refs) > 0:
					X.append(mention_refs)
					gender=self.gender_pronouns[tok.lower()]
					Y.append([gender])

		else:
			for idx, tokenObject in enumerate(toks):
				tok=tokenObject.text
				if tok.lower() in self.gender_pronouns:

					mentions=self.get_mentions(loc_starts, idx)
					mention_refs=[]
					for start, end, loc_idx, text in mentions:
						mention_refs.append(text.lower())

					if len(mention_refs) > 0:
						X.append(mention_refs)
						gender=self.gender_pronouns[tok.lower()]
						Y.append([gender])


		return X, Y




	def read_tokens(self, tokenFile):
		toks=[]
		with open(tokenFile) as file:
			for line in file:
				cols=line.rstrip().split("\t")

				paragraph_id=int(cols[0])
				sentence_id=int(cols[1])
				index_within_sentence_idx=int(cols[2])
				token_id=int(cols[3])
				text=cols[4]
				lemma=cols[5]
				startByte=int(cols[6])
				pos=cols[8]
				deprel=cols[9]
				dephead=int(cols[10])
				ner=None

				tok=Token(paragraph_id, sentence_id, index_within_sentence_idx, token_id, text, pos, None, lemma, deprel, dephead, ner, startByte)

				toks.append(tok)

		return toks


	def read_entities(self, entityFile):

		entities=[]

		with open(entityFile) as file:

			for line in file:
				cols=line.rstrip().split("\t")
				start=int(cols[0])
				end=int(cols[1])
				prop=cols[2]
				cat=cols[3]
				cat="%s_%s" % (prop, cat)
				text=cols[4]

				entities.append((start, end, cat, text))

		return entities


	def update_gender_from_coref(self, genders, entities, corefs):

		counts={}

		for idx, (start, end, cat, text) in enumerate(entities):
			coref=corefs[idx]
			if coref not in counts:
				counts[coref]={}

			for gc in self.genders:
				for term in gc:
					if text.lower() == term:
						key='/'.join(gc)
						if key not in counts[coref]:
							counts[coref][key]=0

						counts[coref][key]+=1

		for c in counts:
			if c not in genders:
			

				total=0
				maxg=None
				maxv=0
				for key in counts[c]:
					total+=counts[c][key]
					if counts[c][key] > maxv:
						maxv=counts[c][key]
						maxg=key

				if total == 0:
					continue

				genders[c]={}
				genders[c]["inference"]={}
				for i in range(self.num_genders):
					genders[c]["inference"][self.reverseID[i]] = 0

				for key in counts[c]:
					genders[c]["inference"][key]=counts[c][key]/total

				if total >0:
					genders[c]["argmax"]=maxg
					genders[c]["max"]=maxv/total
					genders[c]["total"]=total


		return genders

if __name__ == "__main__":

	top=sys.argv[1]
	outfile=sys.argv[2]
	hyperparams=None
	if len(sys.argv) > 3:
		hyperparams=sys.argv[3]
	onlyfiles = [f for f in listdir(top)]
	num=len(onlyfiles)

	ent_files=[]
	tok_files=[]
	for idd in (onlyfiles[:num]):
		entitiyFile=os.path.join(top, idd, "%s.entities" % idd)
		tokensFile=os.path.join(top, idd, "%s.tokens" % idd)
		if isfile(entityFile) and isfile(tokensFile):
			ent_files.append(entityFile)
			tok_files.append(tokensFile)

	genders=[ ["he", "him", "his"], ["she", "her"], ["they", "them", "their"] ] 
	genderEM=GenderEM(outfile=outfile, entityFiles=ent_files, tokenFiles=tok_files, hyperparameterFile=hyperparams, genders=genders)
	genderEM.tagFromFile(ent_files, tok_files)

