import sys
import numpy as np

def get_accuracy(golds, preds, tagset):
	cor=0.
	tot=0.
	for i in range(len(golds)):
		if golds[i] == preds[i]:
			cor+=1
		tot+=1

	acc=cor/tot
	print ("Accuracy: %.3f" % acc)

	return acc


def check_span_f1_two_dicts_subcat(gold, pred):


	golds={}
	preds={}

	for target_lab in ["PRON", "NOM", "PROP"]:
		golds[target_lab]={}
		preds[target_lab]={}
		
		for doc, lab, start, end in gold:
			# print(lab)
			subcat=lab.split("_")[0]
			if subcat == target_lab:
				golds[target_lab][(doc, lab, start, end)]=1

		for doc, lab, start, end in pred:
			subcat=lab.split("_")[0]
			if subcat == target_lab:
				preds[target_lab][(doc, lab, start, end)]=1
			
	cor=0.
	for g in gold:
		if g in pred:
			cor+=1

	precision=0
	if len(pred) > 0:
		precision=cor/len(pred)
	recall=0
	if len(gold) > 0:
		recall=cor/len(gold)
	mainF=0
	if (precision + recall) > 0:
		mainF=(2*precision*recall)/(precision+recall)

	print ("precision: %.3f %s/%s" % (precision, cor, len(pred)))
	print ("recall: %.3f %s/%s" % (recall, cor, len(gold)))
	print ("F: %.3f" % mainF)


	for target_lab in ["PRON", "NOM", "PROP"]:
		cor=0.
		for g in golds[target_lab]:
			if g in preds[target_lab]:
				cor+=1

		precision=0
		if len(preds[target_lab]) > 0:
			precision=cor/len(preds[target_lab])
		recall=0
		if len(golds[target_lab]) > 0:
			recall=cor/len(golds[target_lab])
		F=0
		if (precision + recall) > 0:
			F=(2*precision*recall)/(precision+recall)

		print ("\n\t%s precision: %.3f %s/%s" % (target_lab, precision, cor, len(preds[target_lab])))
		print ("\t%s recall: %.3f %s/%s" % (target_lab, recall, cor, len(golds[target_lab])))
		print ("\t%s F: %.3f" % (target_lab, F))


	return mainF


def check_span_f1_two_dicts(gold, pred):

	cor=0.
	for g in gold:
		if g in pred:
			cor+=1

	precision=0
	if len(pred) > 0:
		precision=cor/len(pred)
	recall=0
	if len(gold) > 0:
		recall=cor/len(gold)
	F=0
	if (precision + recall) > 0:
		F=(2*precision*recall)/(precision+recall)

	print ("precision: %.3f %s/%s" % (precision, cor, len(pred)))
	print ("recall: %.3f %s/%s" % (recall, cor, len(gold)))
	print ("F: %.3f" % F)

	return F

def check_span_f1_two_lists(gold, preds, orig_tagset):

	tagset={orig_tagset[v]:v for v in orig_tagset}
	print(tagset)
	start_idx=-1
	start_tag=None

	gold_spans={}

	for i, tag_idx in enumerate(gold):
		tag=tagset[int(tag_idx)]
		if tag == "O" or tag.startswith("B-"):
			if start_idx != -1:
				end_idx=i-1
				gold_spans[(start_idx, end_idx, start_tag)]=1
				start_idx=-1

		if tag.startswith("B-"):
			start_idx=i
			start_tag=tag.split("-")[-1]

	if start_idx != -1:
		end_idx=len(gold)
		gold_spans[(start_idx, end_idx, start_tag)]=1


	start_idx=-1
	start_tag=None

	pred_spans={}

	for i, tag_idx in enumerate(preds):
		tag=tagset[int(tag_idx)]
		if tag == "O" or tag.startswith("B-"):
			if start_idx != -1:
				end_idx=i-1
				pred_spans[(start_idx, end_idx, start_tag)]=1
				start_idx=-1

		if tag.startswith("B-"):
			start_idx=i
			start_tag=tag.split("-")[-1]

	if start_idx != -1:
		end_idx=len(gold)
		pred_spans[(start_idx, end_idx, start_tag)]=1

	correct=0.
	for tag in gold_spans:
		if tag in pred_spans:
			correct+=1


	trials=len(pred_spans)
	trues=len(gold_spans)

	p=0
	if trials > 0:
		p=correct/trials
	r=0
	if trues > 0:
		r=correct/trues

	f=0
	if (p+r) > 0:
		f=(2*p*r)/(p+r)

	print ("precision: %.3f %s/%s" % (p, correct, trials))
	print ("recall: %.3f %s/%s" % (r, correct, trues))
	print ("F: %.3f" % f)

	return f

def check_f1_two_lists(gold, preds, tagset):

	correct=0.
	trials=0.
	trues=0.
	for j in range(len(preds)):
		if preds[j] == 1:
			trials+=1
		if gold[j] == 1:
			trues+=1
		if preds[j] == gold[j] and preds[j] == 1:
			correct+=1

	p=0
	if trials > 0:
		p=correct/trials
	r=0
	if trues > 0:
		r=correct/trues

	f=0
	if (p+r) > 0:
		f=(2*p*r)/(p+r)

	print ("precision: %.3f %s/%s" % (p, correct, trials))
	print ("recall: %.3f %s/%s" % (r, correct, trues))
	print ("F: %.3f" % f)

	return f


def check_f1(data):
	correct=0.
	trials=0.
	trues=0.

	for sentence in data:
		for word in sentence:
			truth=word[0]
			pred=word[1]

			if pred == 1:
				trials+=1
			if truth == 1:
				trues+=1
			if pred == truth and pred == 1:
				correct+=1

	p=0.
	if trials > 0:
		p=correct/trials
	r=0.
	if trues > 0:
		r=correct/trues

	f=0.
	if (p+r) > 0:
		f=(2*p*r)/(p+r)

	return f, p, r, correct, trials, trues


