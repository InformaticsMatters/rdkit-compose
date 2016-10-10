from django.shortcuts import render
import urllib
from django.http import HttpResponse
from rdkit_screen.functions import SimMethods, LibMethods, FPMethods
from rdkit import Chem
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page
from json_function.json_parse import remove_keys
import ast
import urllib2
from mol_parsing.functions import request_handler, process_input
import CloseableQueue
import json

def index(request):
    out_d = [
    {
    "id":"rdkit.screening.simple",
    "name":"RDKit screening",
    "description":"RDKit simple descriptor based screening",
    "tags":["virtualscreening", "screening", "moleculardescriptors", "fingerprints", "rdkit"],
    "inputClass":"org.squonk.types.MoleculeObject",
    "outputClass":"org.squonk.types.MoleculeObject",
    "inputType":"STREAM",
    "outputType":"STREAM",
    "icon": "icons/filter_molecules.png",
    "executionEndpoint":"screen_simple",
    "endpointRelative":True,
    "options":[
            {
            "editable": True,
            "visible": True,
            "description": "Structure to use for the query",
            "label": "Query Structure",
            "key": "query.structure",
            "typeDescriptor": {
              "type": "org.squonk.options.types.Structure",
              "formats": ["smiles"],        
              "molType": "DISCRETE",
              "@class": "org.squonk.options.MoleculeTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
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
            "visible": False,
            "defaultValue": "application/json",
            "description": "Content-Type header",
            "label": "Content-Type",
            "key": "header.Content-Type",
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": False,
            "visible": False,
            "defaultValue": "application/json",
            "description": "Accept header",
            "label": "Accept",
            "key": "header.Accept",
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "defaultValue": True,
            "description": "Not all inputs are returned",
            "label": "Filter results",
            "key": "option.filter",
            "typeDescriptor": {
              "type": "java.lang.Boolean",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": False,
            "visible": False,
            "defaultValue": False,
            "description": "Streaming supported (not in this case)",
            "label": "Streaming supported",
            "key": "streamsupport",
            "typeDescriptor": {
              "type": "java.lang.Boolean",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            }
        ],
        "executorClassName":"org.squonk.execution.steps.impl.MoleculeServiceThinExecutorStep"
    }]
    return HttpResponse(json.dumps(out_d))


@gzip_page
@csrf_exempt
def screen_simple(request):
    """View to take a smiles and then screen against a known library"""
    import urllib
    # Take the smiles in the request object
    # Now get the library
    if "dump_out" in request.GET:
        return HttpResponse(json.dumps(str(request))+"\nBODY:" + request.body)
    mol_type, screen_lib, fp_method, sim_method, threshold, params = request_handler(request)
    if "structure_source" in request.GET:
        smiles = request.GET["structure_source"]
        scr_mols = CloseableQueue.CloseableQueue()
        [scr_mols.put({"RDMOL": Chem.MolFromSmiles(str(x))}) for x in str(smiles).split(".")]
        scr_mols.close()
    else:
    	# TODO - work out how to throw this as 400 error - doing the obvious doesn't seem to work
    	print "No smiles specified as parameter structure_source"
        return HttpResponse("You must specify a structure as SMILES with the parameter structure_source")
    # Now handle this file upload 
    return process_input(fp_method, sim_method, screen_lib, mol_type, threshold, params=None, scr_mols=scr_mols)
