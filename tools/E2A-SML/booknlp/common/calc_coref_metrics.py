import subprocess, re, sys

def get_coref_score(metric, path_to_scorer, gold=None, preds=None):

	output=subprocess.check_output(["perl", path_to_scorer, metric, preds, gold]).decode("utf-8")
	output=output.split("\n")[-3]
	matcher=re.search("Coreference: Recall: \(.*?\) (.*?)%	Precision: \(.*?\) (.*?)%	F1: (.*?)%", output)
	if matcher is not None:
		recall=float(matcher.group(1))
		precision=float(matcher.group(2))
		f1=float(matcher.group(3))
	return recall, precision, f1

def get_conll(path_to_scorer, gold=None, preds=None):
	bcub_r, bcub_p, bcub_f=get_coref_score("bcub", path_to_scorer, gold, preds)
	muc_r, muc_p, muc_f=get_coref_score("muc", path_to_scorer, gold, preds)
	ceaf_r, ceaf_p, ceaf_f=get_coref_score("ceafe", path_to_scorer, gold, preds)

	print("bcub:\t%.1f" % bcub_f)
	print("muc:\t%.1f" % muc_f)
	print("ceaf:\t%.1f" % ceaf_f)
	avg=(bcub_f + muc_f + ceaf_f)/3.
	print("Average F1: %.1f" % (avg))

	# Generate Latex table
	# print("%.1f&%.1f&%.1f&%.1f" % (bcub_f, muc_f, ceaf_f, avg))

	return bcub_f, avg

if __name__ == "__main__":

	goldFile=sys.argv[1]
	predFile=sys.argv[2]
	scorer=sys.argv[3]
	bcub_f, avg=get_conll(scorer, gold=goldFile, preds=predFile)
	

	