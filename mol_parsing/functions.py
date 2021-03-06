import ast
from threading import Thread
import urllib,zlib
from rdkit_screen.functions import SimMethods, LibMethods, FPMethods
from rdkit_cluster.functions import ClusterMethods
from rdkit import Chem
import json, gzip
from rdkit.ML.Cluster import Butina
from rdkit.ML.Cluster import Butina
from django.http import HttpResponse, StreamingHttpResponse
from django.http import HttpResponseServerError
from json_function.json_parse import remove_keys
import CloseableQueue
from StringIO import StringIO
from CloseableQueue import Closed
import copy


def do_screen(simm, screen_fps, threshold, mol_fps):
    """Function to peform a scren on a library of mols"""
    # Store the result in this
    out_d = {}
    # There are potentially multiple - but here we consider one only
    while True:
        try:
            mol = mol_fps.get()
        except Closed:
            break
        out_mols = simm.find_sim(mol, screen_fps, threshold)
        # The mol(1) is the smiles of the mol
        out_d = remove_keys(out_mols)
        mol_fps.task_done()
        # Now return - preferably as json
        return HttpResponse(json.dumps(out_d))


def do_clustering(simm, queue_fps, threshold):
    """Function to peform the clustering for a library"""
    # Now produce the distance matric
    dists = []
    screen_fps = []
    while True:
        try:
            screen_fps.append(queue_fps.get())
        except Closed:
            break
    nfps = len(screen_fps)
    for i in range(1, nfps):
        other_mols_to_scr = CloseableQueue.CloseableQueue()
        # Make the queues
        [other_mols_to_scr.put(x) for x in screen_fps[:i]]
        other_mols_to_scr.close()
        sims = [x["values"]["similarity"] for x in simm.find_sim(screen_fps[i], other_mols_to_scr, -1.0)]
        # The mol(1) is the smiles of the mol
        dists.extend([1 - x for x in sims])
    # now cluster the data:
    cs = Butina.ClusterData(dists, nfps, threshold, isDistData=True)
    # Out mols is the list for caputring the clusters
    out_mols = []
    # Now loop through the clusters outputing the results
    for i, c in enumerate(cs):
        for mol_ind in c:
            my_mol = screen_fps[mol_ind]
            my_mol["values"]["cluster"] = i
            out_mols.append(my_mol)
    # Now return the response
    return HttpResponse(json.dumps(remove_keys(out_mols)))


def process_input(fp_method, sim_method, screen_lib, screen_type, threshold, params=None, scr_mols=None):
    # Now run the process
    # Get the library
    # Get the fps
    if screen_lib is None:
        return HttpResponse(screen_type)
    libm = LibMethods(screen_lib, screen_type)
    if libm.lib_type is None:
        return HttpResponse("NOT RECOGNISED UPLOAD TYPE" + screen_type)
    mols = CloseableQueue.CloseableQueue()
    ## START IN THREAD
    #libm.get_mols(mols)
    thread = Thread(target=libm.get_mols, args=(mols,))
    thread.start()
    fpm = FPMethods(fp_method)
    if not fpm.fp_method:
        return HttpResponseServerError("NOT A REGISTERED FINGERPRINT METHOD -> " + fp_method)
    # Now get the fingerprints
    screen_fps = CloseableQueue.CloseableQueue()
    ### EXECUTE IN THREAD
    #fpm.get_fps(mols, screen_fps)
    thread = Thread(target=fpm.get_fps, args=(mols, screen_fps))
    thread.start()
#    if not screen_fps:
#        return HttpResponse("ERROR PRODUCING FINGERPRINTS (FOR SCREENING LIBRARY)")
    # Now get the similarity metric
    simm = SimMethods(sim_method)
    if not simm.sim_meth:
        return HttpResponseServerError("NOT A VALID SIMILARIY METRIC")
    if scr_mols:
        mol_fps = CloseableQueue.CloseableQueue()
        fpm.get_fps(scr_mols, mol_fps)
#        if not mol_fps:
#            return HttpResponse("ERROR PRODUCING FINGERPRINTS (FOR MOLECULES)")
#        else:
        return do_screen(simm, screen_fps, threshold, mol_fps)
    else:
        return do_clustering(simm, screen_fps, threshold)


def find_lib_type(request):
    """Function to handle different types of incoming molecule libraries"""
    #for key in request.META:
    #	if key.startswith("HTTP") or key == "CONTENT_TYPE" or key == "CONTENT_LENGTH":
    #		print "Meta:",key," -> ",request.META[key]
    body = request.read()
    print "Body length:", len(body)
    if "HTTP_CONTENT_ENCODING" in request.META:
        if request.META["HTTP_CONTENT_ENCODING"] == "gzip":
            compressedFile = StringIO(body)
            decompressedFile = gzip.GzipFile(fileobj=compressedFile)
            data = decompressedFile.read()
        else:
            print "NOT VALID INPUT ENCODING"
            return None, "DISALLOWED ENCODING TYPE"
    else:
        #data = urllib.unquote(request.body).decode('utf8')
        data = body #.decode('utf8')
    #print "data:", data
    if request.META["CONTENT_TYPE"] == "application/json":
        try:
            screen_lib = ast.literal_eval(data)
            mol_type = "JSON"
        except:
            print "NOT VALID JSON:"
            return None, "NOT VALID JSON"
    elif request.META["CONTENT_TYPE"] == "chemical/x-mdl-sdfile":
        screen_lib = data
        mol_type = "SDF"
    else:
        try:
            screen_lib = dict(request.POST).keys()[0]
            screen_lib = ast.literal_eval(str(screen_lib))
            mol_type = "JSON"
        except IndexError:
            return None, "NONE OR DISALLOWED CONTENT TYPE"
    return screen_lib, mol_type



def request_handler(request):
    """Function to handle a generic request"""
    # Now handle this file upload 
    screen_lib, mol_type = find_lib_type(request)
    # Make the fingerprints
    if "fp_method" in request.GET:
        fp_method = request.GET["fp_method"]
    else:
        fp_method = "morgan"
    if "params" in request.GET:
        params = request.GET["params"].split(",")
    else:
        params = None
    if "sim_method" in request.GET:
        sim_method = request.GET["sim_method"]
    else:
        sim_method = "tanimoto"
    if "threshold" in request.GET:
        threshold = float(request.GET["threshold"])
    else:
        threshold = 0.7
    return mol_type, screen_lib, fp_method, sim_method, threshold, params 
    
  
#def to_bool(value):
#	if value:
#		if str(value).lower() in ("yes", "y", "true",  "t", "1"): 
#			return True
#	return False
    
def read_input(request):
    if "HTTP_CONTENT_ENCODING" in request.META:
        if request.META["HTTP_CONTENT_ENCODING"] == "gzip":
			data = gzip.GzipFile(fileobj=StringIO(request.read()))
        else:
            print "NOT VALID INPUT ENCODING"
            return None, "DISALLOWED ENCODING TYPE"
    else:
        data = request
    return data, "JSON"
    
def write_json_results(items):
	print "Writing results"
	yield "[\n"
	count = 0
	for item in items:
		#print "writing...",count+1
		if count == 0:
			yield json.dumps(item)
		else: 	
			yield ",\n" + json.dumps(item)
		count +=1
	yield "\n]"
	print count,"results generated"
	
def write_results(items):
	return StreamingHttpResponse(write_json_results(items))
	
#class IterEncoder(json.JSONEncoder):
#	"""Allows iterator to be encoded as json.
#	Taken from http://code.davidjanes.com/blog/2008/12/08/json-encode-iterators/
#	"""
#	def default(self, o):
#		try:
#			return  json.JSONEncoder.default(self, o)
#		except TypeError, x:
#			try:
#				return  list(o)
#			except:
#				return  x

#def generate_output(results):
#	iter = CloseableQueue.dequeue(results)
#	return HttpResponse(json.dumps(iter, cls = IterEncoder), content_type='application/json')


