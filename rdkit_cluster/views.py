# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from rdkit_screen.functions import SimMethods, LibMethods, FPMethods
from rdkit_cluster.functions import ClusterMethods
from rdkit import Chem
import json, gzip
from rdkit.ML.Cluster import Butina
from StringIO import StringIO
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page
from json_function.json_parse import remove_keys
import ast
import urllib2
import urllib
from mol_parsing.functions import request_handler, process_input
import json

def index(request):
    out_d = [
    {
    "id":"rdkit.clustering.simple",
    "name":"RDKit clustering",
    "description":"RDKit simple descriptor based clustering",
    "tags":["clustering","rdkit"],
    "icon": "icons/clustering.png",
    "paths":["/Chemistry/Toolkits/RDKit/Clustering","/Chemistry/Clustering"],
    "owner":"Tim Dudgeon <tdudgeon@informaticsmatters.com>",
    "layers":["public"],
    "inputClass":"com.im.lac.types.MoleculeObject",
    "outputClass":"com.im.lac.types.MoleculeObject",
    "inputType":"STREAM",
    "outputType":"STREAM",
    "accessModes":[
    {
        "id":"asyncHttp",
        "name":"Immediate execution",
        "description":"Execute as an asynchronous REST web service",
        "executionEndpoint":"cluster_simple",
        "endpointRelative":True,
        "jobType":"com.im.lac.job.jobdef.AsyncHttpProcessDatasetJobDefinition",
        "parameters":[
            {
            "editable": True,
            "visible": True,
            "defaultValue": 0.7,
            "description": "Similarity score cuttoff between 0 and 1 (1 means identical)",
            "label": "Similarity Cuttoff",
            "key": "query.threshold",
            "typeDescriptor": {
              "type": "java.lang.Float",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "defaultValue": "morgan",
            "values": ["morgan","maccs","rdkit_topo","atom_pairs"],
            "description": "Fingerprint method",
            "label": "Fingerprint",
            "key": "query.fp_method",
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "defaultValue": "tanimoto",
            "values": ["tanimoto","cosine","dice","tversky"],
            "description": "Similarity comparison metric",
            "label": "Metric",
            "key": "query.metric",
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": False,
            "visible": True,
            "defaultValue": "application/json",
            "description": "Content-Type header",
            "label": "Content-Type",
            "key": "header.Content-Type",
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            }
        ],
        "adapterClassName":"com.im.lac.services.job.service.adapters.HttpGenericParamsJobAdapter"
    }
    ]
    }
    ]
    return HttpResponse(json.dumps(out_d))

@gzip_page
@csrf_exempt
def cluster_simple(request):
        # Read the mols
    # Take the smiles in the request object
    if "dump_out" in request.GET:
        return HttpResponse(json.dumps(str(request))+"\nBODY:" + request.body)
    mol_type, screen_lib, fp_method, sim_method, threshold, params = request_handler(request)
    # Now return the process
    return process_input(fp_method, sim_method, screen_lib, mol_type, threshold, params)
