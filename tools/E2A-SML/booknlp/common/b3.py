import sys

def b3(gold, system):

	goldClusters={}
	for key in gold: 
		entity_id=gold[key]
		if entity_id not in goldClusters:
			goldClusters[entity_id]=[]
		goldClusters[entity_id].append(key)

	systemClusters={}
	for key in system: 
		entity_id=system[key]
		if entity_id not in systemClusters:
			systemClusters[entity_id]=[]
		systemClusters[entity_id].append(key)

	precision=0.
	recall=0.

	bigP=0.
	bigR=0.
	n=0.

	for mention in gold:

		goldCluster=set(goldClusters[gold[mention]])
		systemCluster=set(systemClusters[system[mention]])
		intersection=float(len(goldCluster.intersection(systemCluster)))

		precision=intersection/len(systemCluster)
		recall=intersection/len(goldCluster)

		bigP+=precision
		bigR+=recall

		n+=1

	precision=bigP/n if n > 0 else 0
	recall=bigR/n if n > 0 else 0
	F=(2*precision*recall)/(precision+recall) if (precision+recall) > 0 else 0


	return precision, recall, F


def read_data(filename):
	gold={}
	system={}

	with open(filename) as file:
		for idx, line in enumerate(file):
			cols=line.rstrip().split("\t")
			gold[idx]=cols[1]
			system[idx]=cols[2]

	return gold, system

if __name__ == "__main__":
	gold, system=read_data(sys.argv[1])
	precision, recall, F=b3(gold, system)
	print("F1: %.3f\tP: %.3f, R: %.3f" % (F, precision, recall))


