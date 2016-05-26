from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import AllChem, TorsionFingerprints
from rdkit.ML.Cluster import Butina
from mol_parsing.functions import find_lib_type, read_input, write_json_results, write_results
from mol_parsing.rdkit_parse import parse_mol_json, generate_mols_from_json
from django.core.exceptions import ValidationError
from threading import Thread
import CloseableQueue
import uuid, collections, json
from django.http import HttpResponse, StreamingHttpResponse



def request_params(request):
    """Function to handle the request parameters"""
    screen_lib, mol_type = read_input(request)
    if "num" in request.GET:
        num = int(request.GET["num"])
    else:
        num = 1
    if "attempts" in request.GET:
        attempts = int(request.GET["attempts"])
        if attempts < num:
        	attempts = num
    else:
        attempts = num
    if "prune" in request.GET:
        prune = float(request.GET["prune"])
    else:
        prune = 0.1
    if "method" in request.GET:
        method = request.GET["method"]
    else:
        method = "RMSD"
    if "threshold" in request.GET:
        threshold = float(request.GET["threshold"])
    else:
        if method == "TFD":
        	threshold = 0.3
        else:
        	threshold = 2.0
    if "minimize" in request.GET:
        minimize = int(request.GET["minimize"])
    else:
        minimize = 0
    return screen_lib, mol_type, num, attempts, prune, method, threshold, minimize
    
def process_mols_conformers(mols, results, num, attempts, prune, method, threshold, minimize):
	idx=0	
	for mol in mols:
		idx+=1
		#print "submitting",idx
		process_mol_conformers(mol, idx, results, num, attempts, prune, method, threshold, minimize)
	print "mols handled:",idx
	results.close()
	

def process_request_conformers(screen_lib, mol_type, num, attempts, prune, method, threshold, minimize):
	mols = generate_mols_from_json(screen_lib)
	results = CloseableQueue.CloseableQueue()
	
	#return StreamingHttpResponse(write_json_results(CloseableQueue.dequeue(results)))
	#return HttpResponse(json.dumps(results))
	
	thread = Thread(target=process_mols_conformers, args=(mols, results, num, attempts, prune, method, threshold, minimize))
	thread.start()
	
	return write_results(CloseableQueue.dequeue(results))

	
def process_mol_conformers(mol, i, results, numConfs, maxAttempts, pruneRmsThresh, clusterMethod, clusterThreshold, minimizeIterations):
	#print "generating conformers for molecule",i
	if mol is None: return
	m = Chem.AddHs(mol)
	# generate the confomers
	conformerIds = gen_conformers(m, numConfs, maxAttempts, pruneRmsThresh, True, True, True)
	conformerPropsDict = {}
	for conformerId in conformerIds:
		# energy minimise (optional) and energy calculation
		props = calc_energy(m, conformerId, minimizeIterations)
		conformerPropsDict[conformerId] = props
	# cluster the conformers
	rmsClusters = cluster_conformers(m, clusterMethod, clusterThreshold)

	print "Molecule", i, "generated", len(conformerIds), "conformers and", len(rmsClusters), "clusters"
	rmsClustersPerCluster = []
	clusterNumber = 0
	minEnergy = 9999999999999
	for cluster in rmsClusters:
		clusterNumber = clusterNumber+1
		rmsWithinCluster = align_conformers(m, cluster)
		for conformerId in cluster:
			e = props["EnergyAbs"]
			if e < minEnergy:
				minEnergy = e
			props = conformerPropsDict[conformerId]
			props["ClusterNum"] = clusterNumber
			props["ClusterCentroid"] = cluster[0] + 1
			idx = cluster.index(conformerId)
			if idx > 0:
				props["RMSToCentroid"] = rmsWithinCluster[idx-1]
			else:
				props["RMSToCentroid"] = 0.0
	
	for id in conformerIds:
		mo = collections.OrderedDict()
		mo["uuid"] = str(uuid.uuid4())
		mo["format"] = "mol"
		mo["source"] = Chem.MolToMolBlock(m, includeStereo=True, confId=id) 
		props = conformerPropsDict[id]
		props["ConformerNum"] = id+1
		props["StructureNum"] = i
		e = props["EnergyAbs"]
		if e:
			props["EnergyDelta"] = e - minEnergy
		props["StructureUUID"] = mol.GetProp("uuid")
		mo["values"] = props
		results.put(mo)

	
	
def gen_conformers(mol, numConfs=100, maxAttempts=1000, pruneRmsThresh=0.1, useExpTorsionAnglePrefs=True, useBasicKnowledge=True, enforceChirality=True):
	ids = AllChem.EmbedMultipleConfs(mol, numConfs=numConfs, maxAttempts=maxAttempts, pruneRmsThresh=pruneRmsThresh, useExpTorsionAnglePrefs=useExpTorsionAnglePrefs, useBasicKnowledge=useBasicKnowledge, enforceChirality=enforceChirality, numThreads=0)
	#print "generated",len(ids),"conformers"
	return list(ids)
	
def calc_energy(mol, conformerId, minimizeIts):
	ff = AllChem.MMFFGetMoleculeForceField(mol, AllChem.MMFFGetMoleculeProperties(mol), confId=conformerId)
	ff.Initialize()
	results = collections.OrderedDict()
	if minimizeIts > 0:
		results["MinimizationConverged"] = ff.Minimize(maxIts=minimizeIts)
	results["EnergyAbs"] = ff.CalcEnergy()
	return results
	
def cluster_conformers(mol, mode="RMSD", threshold=2.0):
	if mode == "TFD":
		dmat = TorsionFingerprints.GetTFDMatrix(mol)
	else:
		dmat = AllChem.GetConformerRMSMatrix(mol, prealigned=False)
	rms_clusters = Butina.ClusterData(dmat, mol.GetNumConformers(), threshold, isDistData=True, reordering=True)
	#print "generated",len(rms_clusters),"clusters"
	return rms_clusters
	
def align_conformers(mol, clust_ids):
	rmslist = []
	AllChem.AlignMolConformers(mol, confIds=clust_ids, RMSlist=rmslist)
	return rmslist

