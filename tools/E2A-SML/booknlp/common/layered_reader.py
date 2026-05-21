import numpy as np
import torch

def get_batches(model, sentences, max_batch, tagset, training=True):

	"""
	Partitions a list of sentences (each a list containing [word, label]) into a set of batches
	Returns:

	-- batched_sents: original tokens in sentences
		
	-- batched_orig_token_lens: length of original tokens in sentences

	-- batched_data: token ids of sentences. [[101 37 42 102], [101 7 102 0]]
	
	-- batched_mask: Binary flag for real tokens (1) and padded tokens (0) [[1 1 1 1], [1 1 1 0]] (for BERT)
	
	-- batched_transforms: BERT word piece tokenization splits words into pieces; this matrix specifies how
	to combine those pieces back into the original tokens (by averaging their representations) using matrix operations.
	If the original sentence is 3 words that have been tokenized into 4 word piece tokens [101 37 42 102] 
	(where 37 42 are the pieces of one original word), the transformation matrix is 4 x 3 (zero padded to 4 x 4), 
	resulting in the original sequence length of 3. [[1 0 0 0], [0 0.5 0.5 0], [0 0 0 1]]. 

	-- batched_labels: Labels for each sentence, one label per original token (prior to word piece tokenization). Padded tokens
		and [CLS] and [SEP] have labels -100.

	-- batched_layered_labels{1,2,3,4,5}: Labels for each sentence, one label per original token (prior to word piece tokenization). Padded tokens and [CLS] and [SEP] have labels -100.

	-- batched_index{1,2,3}: For nested NER, words that are part of the same entity in layer n are merged together in layer n+1. batched_index is a matrix that specifies how to combine those token representations when moving between layers.  The matrix is 0-padded to be square in the length of the input layer.
	
	-- batched_newlabel{1,2,3}.  batched_labels (above) specifies the labels for each absolute token position; for nested NER, however, the sequence length gets smaller when moving from lower layers to higher layers (since tokens within the same entity are combined).  batched_newlabel specifies the correct labels for the actual sequence length in a given layer.  Padded to the max sequence length for a batch with -100.

	-- batched_lens{1,2,3}: The actual sequence length in a given layer.

	-- ordering: inverse argsort to recover original ordering of sentences.

	"""

	rev_tagset={tagset[v]:v for v in tagset}

	maxLen=0

	all_sents=[]
	all_orig_token_lens=[]

	for sentence in sentences:
		length=0
		# ts=[x[0] for x in sentence]
		ts=[' '.join(x) for x in sentence]
		all_sents.append(ts)

		all_orig_token_lens.append(len(sentence))

		for toks in sentence:
			# toks=model.tokenizer.tokenize(word[0])
			length+=len(toks)

		if length > maxLen:
			maxLen=length

	all_data=[]
	all_masks=[]
	all_labels=[]


	all_layered_labels1=[]
	all_layered_labels2=[]
	all_layered_labels3=[]
	all_layered_labels4=[]
	all_layered_labels5=[]
	
	all_indices=[]
	all_newlabels=[]

	all_transforms=[]

	for sentence in sentences:
		tok_ids=[]
		input_mask=[]
		labels=[]

		layered_labels1=[]
		layered_labels2=[]
		layered_labels3=[]
		layered_labels4=[]
		layered_labels5=[]
		
		transform=[]

		all_toks=[]
		n=0
		for idx, toks in enumerate(sentence):
			# toks=model.tokenizer.tokenize(word[0])
			all_toks.append(toks)
			n+=len(toks)

		cur=0
		for idx, word in enumerate(sentence):
			toks=all_toks[idx]
			ind=list(np.zeros(n))
			for j in range(cur,cur+len(toks)):
				ind[j]=1./len(toks)
			cur+=len(toks)
			transform.append(ind)

			tok_ids.extend(model.tokenizer.convert_tokens_to_ids(toks))

			input_mask.extend(np.ones(len(toks)))

			if training:

				labels.append(int(word[1]))
				layered_labels1.append(int(word[1]))
				layered_labels2.append(int(word[2]))
				layered_labels3.append(int(word[3]))
				layered_labels4.append(int(word[4]))
				layered_labels5.append(int(word[5]))

		all_data.append(tok_ids)
		all_masks.append(input_mask)
		all_transforms.append(transform)

		if training:

			all_labels.append(labels)
			all_layered_labels1.append(layered_labels1)
			all_layered_labels2.append(layered_labels2)
			all_layered_labels3.append(layered_labels3)
			all_layered_labels4.append(layered_labels4)
			all_layered_labels5.append(layered_labels5)

			newlabels=model.compress([layered_labels1, layered_labels2, layered_labels3])
			indices=model.get_index(newlabels)
			
			all_indices.append(indices)
			all_newlabels.append(newlabels)


	lengths = np.array([len(l) for l in all_data])
	ordering = np.argsort(lengths)
	ordered_data = [None for i in range(len(all_data))]
	ordered_masks = [None for i in range(len(all_data))]
	ordered_transforms = [None for i in range(len(all_data))]
	orig_sents = [None for i in range(len(all_data))]
	orig_token_lens = [None for i in range(len(all_data))]

	if training:

		ordered_labels = [None for i in range(len(all_data))]
		ordered_layered_labels1 = [None for i in range(len(all_data))]
		ordered_layered_labels2 = [None for i in range(len(all_data))]
		ordered_layered_labels3 = [None for i in range(len(all_data))]
		ordered_layered_labels4 = [None for i in range(len(all_data))]
		ordered_layered_labels5 = [None for i in range(len(all_data))]

		ordered_indices = [None for i in range(len(all_data))]
		ordered_newlabels = [None for i in range(len(all_data))]

	for i, ind in enumerate(ordering):
		ordered_data[i] = all_data[ind]
		ordered_masks[i] = all_masks[ind]
		orig_sents[i]=all_sents[ind]
		orig_token_lens[i]=all_orig_token_lens[ind]
		ordered_transforms[i] = all_transforms[ind]

		if training:

			ordered_labels[i] = all_labels[ind]
			ordered_layered_labels1[i] = all_layered_labels1[ind]
			ordered_layered_labels2[i] = all_layered_labels2[ind]
			ordered_layered_labels3[i] = all_layered_labels3[ind]
			ordered_layered_labels4[i] = all_layered_labels4[ind]
			ordered_layered_labels5[i] = all_layered_labels5[ind]

			ordered_indices[i] = all_indices[ind]
			ordered_newlabels[i] = all_newlabels[ind]

	batched_data=[]
	batched_mask=[]
	batched_labels=[]
	batched_transforms=[]
	batched_indices=[]
	batched_layered_labels1=[]
	batched_layered_labels2=[]
	batched_layered_labels3=[]
	batched_layered_labels4=[]
	batched_layered_labels5=[]
	
	batched_index1=[]
	batched_index2=[]
	batched_index3=[]

	batched_newlabel1=[]
	batched_newlabel2=[]
	batched_newlabel3=[]

	batched_sents=[]
	batched_orig_token_lens=[]

	batched_lens1=[]
	batched_lens2=[]
	batched_lens3=[]

	i=0

	current_batch=max_batch
	order_to_batch_map=[]
	batch_num=0

	while i < len(ordered_data):

		for j in range(current_batch):
			order_to_batch_map.append((batch_num, current_batch, j))

		batch_num+=1

		batch_data=ordered_data[i:i+current_batch]
		batch_mask=ordered_masks[i:i+current_batch]
		batch_sents=orig_sents[i:i+current_batch]
		batch_orig_lens=orig_token_lens[i:i+current_batch]
		batch_transforms=ordered_transforms[i:i+current_batch]
		
		max_len = max([len(sent) for sent in batch_data])
		max_label_length = max([l for l in batch_orig_lens])

		if training:

			batch_labels=ordered_labels[i:i+current_batch]
			
			batch_layered_labels1=ordered_layered_labels1[i:i+current_batch]
			batch_layered_labels2=ordered_layered_labels2[i:i+current_batch]
			batch_layered_labels3=ordered_layered_labels3[i:i+current_batch]
			batch_layered_labels4=ordered_layered_labels4[i:i+current_batch]
			batch_layered_labels5=ordered_layered_labels5[i:i+current_batch]

			batch_indices=ordered_indices[i:i+current_batch]
			batch_newlabels=ordered_newlabels[i:i+current_batch]


		batch_index1=[]
		batch_index2=[]
		batch_index3=[]
		
		batch_new_label1=[]
		batch_new_label2=[]
		batch_new_label3=[]

		lens1=[]
		lens2=[]
		lens3=[]

		for j in range(len(batch_data)):
			
			blen=len(batch_data[j])

			for k in range(blen, max_len):
				batch_data[j].append(0)
				batch_mask[j].append(0)
				for z in range(len(batch_transforms[j])):
					batch_transforms[j][z].append(0)

			for k in range(len(batch_transforms[j]), max_label_length):
				batch_transforms[j].append(np.zeros(max_len))

			if training:

				blab=len(batch_labels[j])
				indexes=batch_indices[j]				
				newlabelz=batch_newlabels[j]

				lens1.append(len(indexes[0][0]))
				lens2.append(len(indexes[1][0]))
				lens3.append(len(indexes[2][0]))

				for k in range(3):
					indexk=indexes[k]

					# pad each row with zeros to the same length
					for y in range(len(indexk)):
						for z in range(len(indexk[y]), max_label_length):
							indexk[y].append(0)

					# pad the matrix with zeros to be square
					for y in range(len(indexk), max_label_length):
						indexk.append(np.zeros(max_label_length))

					# pad the reduced labels with -100
					for z in range(len(newlabelz[k]), max_label_length):
						newlabelz[k].append(-100)

				batch_index1.append(indexes[0])
				batch_index2.append(indexes[1])
				batch_index3.append(indexes[2])

				batch_new_label1.append(newlabelz[0])
				batch_new_label2.append(newlabelz[1])
				batch_new_label3.append(newlabelz[2])


				for k in range(blab, max_label_length):
					batch_labels[j].append(-100)

					batch_layered_labels1[j].append(-100)
					batch_layered_labels2[j].append(-100)
					batch_layered_labels3[j].append(-100)
					batch_layered_labels4[j].append(-100)
					batch_layered_labels5[j].append(-100)



		batched_data.append(torch.LongTensor(batch_data))
		batched_mask.append(torch.FloatTensor(batch_mask))
		batched_sents.append(batch_sents)
		batched_orig_token_lens.append(torch.LongTensor(batch_orig_lens))

		batched_transforms.append(torch.FloatTensor(np.array(batch_transforms)))

		if training:

			batched_labels.append(torch.LongTensor(batch_labels))

			batched_layered_labels1.append(torch.LongTensor(batch_layered_labels1))
			batched_layered_labels2.append(torch.LongTensor(batch_layered_labels2))
			batched_layered_labels3.append(torch.LongTensor(batch_layered_labels3))
			batched_layered_labels4.append(torch.LongTensor(batch_layered_labels4))
			batched_layered_labels5.append(torch.LongTensor(batch_layered_labels5))

			batched_index1.append(torch.FloatTensor(batch_index1))
			batched_index2.append(torch.FloatTensor(batch_index2))
			batched_index3.append(torch.FloatTensor(batch_index3))


			batched_newlabel1.append(torch.LongTensor(batch_new_label1))
			batched_newlabel2.append(torch.LongTensor(batch_new_label2))
			batched_newlabel3.append(torch.LongTensor(batch_new_label3))

		batched_lens1.append(torch.LongTensor(lens1))
		batched_lens2.append(torch.LongTensor(lens2))
		batched_lens3.append(torch.LongTensor(lens3))
		
		i+=current_batch

		if max_len > 100:
			current_batch=12
		if max_len > 200:
			current_batch=6
	
	
	if training:
		return batched_sents, batched_data, batched_mask, batched_labels, batched_transforms, ordering, batched_layered_labels1, batched_layered_labels2, batched_layered_labels3, batched_layered_labels4, batched_layered_labels5, batched_index1, batched_index2, batched_index3, batched_newlabel1, batched_newlabel2, batched_newlabel3, [batched_lens1, batched_lens2, batched_lens3]

		
	return batched_sents, batched_data, batched_mask, batched_transforms, batched_orig_token_lens, ordering, order_to_batch_map

