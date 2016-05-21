from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import FilterCatalog
import json
from mol_parsing.functions import find_lib_type
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import CloseableQueue
from CloseableQueue import Closed


params = FilterCatalog.FilterCatalogParams()
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A)
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B)
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C)
catalog = FilterCatalog.FilterCatalog(params)

class IterEncoder(json.JSONEncoder):
	"""Allows iterator to be encoded as json.
	Taken from http://code.davidjanes.com/blog/2008/12/08/json-encode-iterators/
	"""
	def default(self, o):
		try:
			return  json.JSONEncoder.default(self, o)
		except TypeError, x:
			try:
				return  list(o)
			except:
				return  x


def request_params(request):
    """Function to handle the request parameters"""
    screen_lib, mol_type = find_lib_type(request)
    if "filter" in request.GET:
        filter = to_bool(request.GET["filter"])
    else:
        filter = 0
    return screen_lib, mol_type, filter

def to_bool(value):
	if value:
		if str(value).lower() in ("yes", "y", "true",  "t", "1"): 
			return True
	return False

def process_pains(mols_q, filter):
	i=0
	results = CloseableQueue.CloseableQueue()
	while True:
		try:
			dict = mols_q.get()
			i +=1
			mol = dict["RDMOL"]
			values = dict["values"]
			uuid = mol.GetProp("uuid")
			mol_result = {}
			mol_result["uuid"] = uuid
			#print "mol",i,uuid
			if catalog.HasMatch(mol):
				if not filter:
					matched_filters = []
					matches = catalog.GetMatches(mol)
					#print "Molecule", i, uuid, "failed", matches.__len__(), "filters"
					for molfilter in matches:
						# get a description of the matching filter
						desc = molfilter.GetDescription()
						#print "  ", desc
						matched_filters.append(desc)
					#matches_str = ",".join(matched_filters)
					values = {}
					size = len(matched_filters)
					values["PainsCount_RDKit"] = size
					if size > 0:
						values["PainsMatches_RDKit"] = matched_filters
						#values["PainsMatchesStr_RDKit"] = matches_str
					mol_result["values"] = values
					results.put(mol_result)
			else:
				if not filter:
					values = {}
					values["PainsCount_RDKit"] = 0
					mol_result["values"] = values
				results.put(mol_result)
			
		except Closed:
			break
	results.close()
	return results
	
def generate_output(results):
	#for o in CloseableQueue.dequeue(results):
	#	print o
	iter = CloseableQueue.dequeue(results)
	return HttpResponse(json.dumps(iter, cls = IterEncoder), content_type='application/json')
	#return HttpResponse("OK Dude!\n")

