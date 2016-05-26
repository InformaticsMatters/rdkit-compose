from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import FilterCatalog
from rdkit.Chem.FilterCatalog import FilterCatalogParams
import json, gzip
from ijson import items
from django.core.exceptions import ValidationError
from threading import Thread
import CloseableQueue
#from multiprocessing.dummy import Pool
from mol_parsing.functions import find_lib_type, read_input, write_json_results, write_results
from mol_parsing.rdkit_parse import parse_mol_json, generate_mols_from_json

from StringIO import StringIO


params = FilterCatalog.FilterCatalogParams()
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_A)
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_B)
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_C)
catalog = FilterCatalog.FilterCatalog(params)



def request_params(request):
    """Function to handle the request parameters"""
    #screen_lib, mol_type = find_lib_type(request)
    screen_lib, mol_type = read_input(request)
    if "filter" in request.GET:
        filter = request.GET["filter"]
        if not (filter == "INCLUDE_MATCHING" or filter == "INCLUDE_NON_MATCHING" or filter == "INCLUDE_ALL"):
        	raise ValidationError("Invalid filter value " + filter)
    else:
        filter = "FILTER_NONE"
    return screen_lib, mol_type, filter


	
def process_mol_pains(mol, queue, filter):
	#print "processing mol"
	uuid = mol.GetProp("uuid")
	mol_result = {}
	mol_result["uuid"] = uuid
	#print "mol",uuid
	if catalog.HasMatch(mol):
		#print "has match"
		if filter == "INCLUDE_ALL" or filter == "INCLUDE_MATCHING":
			matched_filters = []
			matches = catalog.GetMatches(mol)
			#print "Molecule", uuid, "failed", matches.__len__(), "filters"
			for molfilter in matches:
				# get a description of the matching filter
				desc = molfilter.GetDescription()
				#print "  ", desc
				matched_filters.append(desc)
				values = {}
				size = len(matched_filters)
				values["PainsCount_RDKit"] = size
				if size > 0:
					values["PainsMatches_RDKit"] = matched_filters
					mol_result["values"] = values
			queue.put(mol_result)
			
	else:
		if filter == "INCLUDE_ALL":
			values = {}
			values["PainsCount_RDKit"] = 0
			mol_result["values"] = values
			queue.put(mol_result)
		elif filter == "INCLUDE_NON_MATCHING":
			queue.put(mol_result)

def process_mols_pains(mols, queue, filter):
	i=0	
	for mol in mols:
		i+=1
		#print "submitting",i
		process_mol_pains(mol, queue, filter)
	print "mols handled:",i
	queue.close()
	
def process_request_pains(screen_lib, mol_type, filter):
	mols = generate_mols_from_json(screen_lib)
	queue = CloseableQueue.CloseableQueue()
	
	thread = Thread(target=process_mols_pains, args=(mols, queue, filter))
	thread.start()
	
	return write_results(CloseableQueue.dequeue(queue))


