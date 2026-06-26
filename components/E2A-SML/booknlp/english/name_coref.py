"""
This code performs name clustering on PROP PER mentions, grouping together different proper names only that refer to the same individual
e.g., Tom, Tom Saywer, Mr. Tom Sawyer, Mr. Sawyer -> TOM SAYWER

"""

from collections import Counter
import sys
import itertools
import pkg_resources

class NameCoref:

	def __init__(self, aliasFile):
		self.honorifics={"mr":1, "mr.":1, "mrs":1, "mrs.":1, "miss":1, "uncle":1, "aunt":1, "lady":1, "lord":1, "monsieur":1, "master":1, "mistress":1}
		self.aliases={}
		with open(aliasFile) as file:
			for line in file:
				cols=line.rstrip().split("\t")
				canonical=cols[0]
				nicknames=cols[1:]
				for nickname in nicknames:

					if nickname.lower() not in self.aliases:
						self.aliases[nickname.lower()]={}
					self.aliases[nickname.lower()][canonical.lower()]=1

	def get_variants(self, parts):
		variants={}
		for i in range(len(parts)):
			if parts[i].lower() not in self.honorifics:
				variants[parts[i]]=1

			for j in range(i+1, len(parts)):
				variants["%s %s" % (parts[i], parts[j])]=1

				for k in range(j+1, len(parts)):
					variants["%s %s %s" % (parts[i], parts[j], parts[k])]=1

					for l in range(k+1, len(parts)):
						variants["%s %s %s %s" % (parts[i], parts[j], parts[k], parts[l])]=1

						for m in range(l+1, len(parts)):
							variants["%s %s %s %s %s" % (parts[i], parts[j], parts[k], parts[l], parts[m])]=1

							for n in range(m+1, len(parts)):
								variants["%s %s %s %s %s %s" % (parts[i], parts[j], parts[k], parts[l], parts[m], parts[n])]=1

								for o in range(n+1, len(parts)):
									variants["%s %s %s %s %s %s %s" % (parts[i], parts[j], parts[k], parts[l], parts[m], parts[n], parts[o])]=1
								


		return variants

	def get_canonical(self, name_tokens):

		"""
		Given a alias dictionary that maps aliases (nicknames, alternative names) to a "canonical" version 
		of the name, return all possible canonical versions of the input

		Alias dictionary:

		Em -> Emily
		Em -> Emma
		The Great Bambino -> Babe Ruth


		Input -> Output

		Em -> [["Emily"], ["Emma"]]
		Em Smith -> [["Emily", "Smith"], ["Emma", "Smith"]]
		The Great Bambino -> [["Babe", "Ruth"]]

		"""

		# first, if a name is a complete match for an alias, just return the canonicals for the alias
		# Em -> ["Emily", "Emma"]
		# The Great Bambino -> ["Babe Ruth"]
		name=' '.join(name_tokens).lower()
		if name in self.aliases:
			vals=[]
			for can in self.aliases[name]:
				vals.append(can.split(" "))
			return vals

		# next, check if any individual part of a name is an alias
		# Em Smith -> ["Emily Smith", "Emma Smith"]
		parts=[]
		for tok in name_tokens:
			if tok.lower() in self.aliases:
				parts.append(list(self.aliases[tok.lower()]))
			else:
				parts.append([tok])
		canonicals=[]

		canonicals=[]
		for i in itertools.product(*parts): 
			canonicals.append(list(i))

		return canonicals

	def name_cluster(self, entities, is_named, existing_refs):

		"""
		Get counts of all unique names (to be used for disambiguation later)
		"""

		uniq=Counter()
		for i, val in enumerate(is_named):
			if val == 1:
				
				# only consider names with fewer than 10 tokens
				# (longer are likely errors and significantly slow down processing)
				if len(entities[i]) < 10:
					name=' '.join(entities[i]).lower()
					if name != "":
						uniq[name]+=1

		
		"""

		Remove names that are complete subsets of others
		
		e.g., if uniq = ["Em Smith", "Em", "Emma Smith", "Tom", "Tom Sawyer"], then remove "Em", "Em Smith" and "Tom".
			* "Tom" is a subset of "Tom Sawyer"
			* "Em" -> "Emma" and "Emily", and "Emma" is a subset of "Emma Smith"
			* "Em Smith" -> "Emma Smith"
		"""

		subsets={}
		for name1 in uniq:
			canonicals1=self.get_canonical(name1.split(" "))
			for canonical1 in canonicals1:
				name1set=set(canonical1)
				for name2 in uniq:

					if name1 == name2:
						continue

					canonicals=self.get_canonical(name2.split(" "))
					for canonical in canonicals:

						name2set=set(canonical)

						if ' '.join(name1set) == ' '.join(name2set):
							continue

						if name1set.issuperset(name2set):
							subsets[name2]=1

		name_subpart_index={}

		"""

		Now map each possible ordered sub-permutation of a canonical name  (from length 1 to n) to its canonical version.
		
		e.g. the canonical name "David Foster Wallace" -> 
		"David Foster Wallace", "David Wallace", "Foster Wallace", "David Foster", "Foster Wallace", "David", "Foster", "Wallace"

		So if we see any of those phrases as names, we know they could refer to the entity "David Foster Wallace"

		This excludes honorifics like "Mr." and "Mrs." from being their own (unigram) variant, but they can appear in other permutations

		e.g. "Mr. Tom Sawyer" ->
		"Mr. Tom Sawyer", "Mr. Tom", "Mr. Sawyer", "Tom Sawyer", "Tom", "Sawyer"
		
		"""

		for ni, name in enumerate(uniq):
			if name in subsets:
				continue

			canonicals=self.get_canonical(name.split(" "))
			for canonical in canonicals:
				variants=self.get_variants(canonical)

				for v in variants:
					if v not in name_subpart_index:
						name_subpart_index[v]={}

					name_subpart_index[v][name]=1


		"""

		Now let's assign each name *mention* to its entity.

		Starting from the first entity to last, we'll look up the possible entities that the canonical version of
		this mention can be a variant of and assign it to the entity that has the highest score.

		The score for an entity is initialized as the mention count of the maximal name 
		("David Foster Wallace" or "Mr. Tom Sawyer" above), but is primarily driven by recency (with the score
		mainly being the location of the last assigned mention of that entity)

		"""

		charids={}
		max_id=1

		if len(existing_refs) > 0:
			max_id=max(existing_refs)+1

		lastSeen={}
		refs=[]
		for i, val in enumerate(is_named):

			if existing_refs[i] != -1:
				refs.append(existing_refs[i])
				continue

			if val == 1:

				canonicals=self.get_canonical(entities[i])
				name=' '.join(entities[i]).lower()

				top=None
				max_score=0

				for canonical in canonicals:
					canonical_name=' '.join(canonical).lower()

					if canonical_name in name_subpart_index:
						for entity in name_subpart_index[canonical_name]:
							score=uniq[entity]
							if entity in lastSeen:
								score+=lastSeen[entity]
							if score > max_score:
								max_score=score
								top=entity

				if top is not None:
					lastSeen[top]=i

					if top not in charids:
						charids[top]=max_id
						max_id+=1
					refs.append(charids[top])

				# this happens if the name is too long (longer than 7 words)
				else:
					refs.append(-1)
			else:
				refs.append(-1)
		return refs

	def calc_overlap(self, small, big):

		overlap=0
		for name in small:
			if name in big:
				overlap+=small[name]

		return overlap/sum(small.values())

	def read_file(self, spanFile):

		entities=[]
		is_named=[]
		with open(spanFile) as file:
			for line in file:
				cols=line.rstrip().split("\t")

				cat=cols[2].split("_")[1]
				prop=cols[2].split("_")[0]
				if prop != "PROP":
					continue
				text=cols[0].split(" ")
				lemma=cols[1]
				entity_pos=cols[3].split(" ")
				if cat == "PER":
					name_filt_pos=[]
					for pidx, pos in enumerate(entity_pos):
						if pos == "NOUN" or pos == "PROPN":
							name_filt_pos.append(text[pidx])

					entities.append(name_filt_pos)
					is_named.append(1)

		return entities, is_named

	def process(self, spanFile):

		entities, is_named=read_file(spanFile)
		cluster(entities, is_named)

	def cluster_identical_propers(self, entities, refs):

		""" Assign all mentions that are identical to the same entity (used in combination with only performing 
		pronominal coreference resolution) """

		max_id=1
		if len(refs) > 0:
			max_id=max(refs)+1

		names={}

		for idx, (s, e, full_cat, name) in enumerate(entities):
			prop=full_cat.split("_")[0]
			cat=full_cat.split("_")[1]
			
			if prop == "PROP" and cat != "PER":
				n=name.lower()
				key="%s_%s_%s" % (n, prop, cat)
				if key not in names:
					names[key]=max_id
					max_id+=1
				refs[idx]=names[key]

		return refs


	def cluster_noms(self, entities, refs):

		""" Assign all nominal mentions that are identical to the same entity (used in combination with only performing 
		pronominal coreference resolution) """

		names={}
		mapper={}

		for idx, (s, e, cat, name) in enumerate(entities):
			prop=cat.split("_")[0]
			if prop == "NOM":
				n=name.lower()
				if n not in names:
					names[n]=refs[idx]
				else:
					mapper[refs[idx]]=names[n]


		for idx, ref in enumerate(refs):
			if ref in mapper:
				refs[idx]=mapper[ref]

		return refs



	def cluster_narrator(self, entities, in_quotes, tokens):

		""" Create an entity for the first-person narrator from all mentiosn of "I", "me", "my" and "myself" outside of quotes """

		narrator_pronouns=set(["i", "me", "my", "myself"])
		refs=[]
		for idx, (s, e, _, name) in enumerate(entities):
			if in_quotes[idx] == 0 and name.lower() in narrator_pronouns:
				refs.append(0)
				# window=25
				# start=max(0, s-window)
				# end=min(e+25, len(tokens))
				# context=[tok.text for tok in tokens[start:end]]
				# print("narrator\t\t", name, ' '.join(context)) 
			else:
				refs.append(-1)
		return refs

	def cluster_only_nouns(self, entities, refs, tokens):

		hon_mapper={"mister":"mr.", "mr.":"mr.", "mr":"mr.", "mistah":"mr.", "mastah":"mr.", "master":"mr.",
		"miss":"miss", "ms.": "miss", "ms":"miss","missus":"miss","mistress":"miss",
		"mrs.":"mrs.", "mrs":"mrs."
		}

		def map_honorifics(term):
			term=term.lower()
			if term in hon_mapper:
				return hon_mapper[term]
			return None

		is_named=[]
		entity_names=[]

		for start, end, cat, text in entities:
			ner_prop=cat.split("_")[0]
			ner_type=cat.split("_")[1]
			if ner_prop == "PROP" and ner_type == "PER":
				is_named.append(1)
			else:
				is_named.append(0)

			new_text=[]
			for i in range(start,end+1):
				hon_mapped=map_honorifics(tokens[i].text)

				if (hon_mapped is not None or (tokens[i].pos == "NOUN" or tokens[i].pos == "PROPN")) and tokens[i].text.lower()[0] != tokens[i].text[0]:
					val=tokens[i].text
					if hon_mapped is not None:
						val=hon_mapped
					new_text.append(val)

			if len(new_text) > 0:
				entity_names.append(new_text)
			else:
				entity_names.append(text.split(" "))

		return self.cluster(entity_names, is_named, refs)

	def cluster(self, entities, is_named, refs):

		refs=self.name_cluster(entities, is_named, refs)
		clusters={}

		for i, val in enumerate(refs):
			ref=refs[i]
			if ref not in clusters:
				clusters[ref]=Counter()
			clusters[ref][' '.join(entities[i])]+=1

		# if two clusters have significant overlap in mention phrases, merge them into one
		for ref in clusters:
			for ref2 in clusters:
				if ref == ref2 or clusters[ref] is None or clusters[ref2] is None or ref == -1 or ref2 == -1 or ref == 0 or ref2 == 0:
					continue

				# find which cluster is bigger and should contain the other
				sum1=sum(clusters[ref].values())
				sum2=sum(clusters[ref2].values())

				big=ref
				small=ref2
				if sum2 > sum1:
					big=ref2
					small=ref

				sim=self.calc_overlap(clusters[small], clusters[big])
				if sim > 0.9:

					for k,v in clusters[small].most_common():
						clusters[big][k]+=v

					for idx, r in enumerate(refs):
						if r == small:
							refs[idx]=big

					clusters[small]=None

		counts=Counter()
		for ref in clusters:
			if clusters[ref] is not None:
				counts[ref]=sum(clusters[ref].values())

		return refs

if __name__ == "__main__":

	aliasFile = pkg_resources.resource_filename(__name__, "data/aliases.txt")
	resolver=NameCoref(aliasFile)
	resolver.process(sys.argv[1])

