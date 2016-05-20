from django.shortcuts import render
import urllib
from django.http import HttpResponse
from rdkit import Chem
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page
from json_function.json_parse import remove_keys
import ast
import urllib2
from mol_parsing.functions import process_input
from rdkit_screen.functions import LibMethods
from rdkit_filter.functions import *
import CloseableQueue

def index(request):
    out_d = [
    {
    "id":"rdkit.filter.pains",
    "name":"PAINS filter (RDKit)",
    "description":"RDKit implementation of PAINS filter",
    "tags":["pains","filter","rdkit"],
    "icon": "icons/filter_molecules.png",
    "paths":["/Chemistry/Toolkits/RDKit/Filter","/Chemistry/Filter"],
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
        "executionEndpoint":"pains",
        "endpointRelative":True,
        "parameters":[
            {
            "editable": True,
            "visible": True,
            "description": "Act as a filter (or add match data to all records)",
            "defaultValue": True,
            "label": "Act as filter (or add match data)",
            "key": "query.filter",
            "typeDescriptor": {
              "type": "java.lang.Boolean",
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
        "adapterClassName":"org.squonk.execution.steps.impl.MoleculeServiceThinExecutorStep"
    }
    ]
    }
    ]
    return HttpResponse(json.dumps(out_d))


@csrf_exempt
def pains(request):
    """View to apply PAINS filters to a library of input molecules"""
    screen_lib, mol_type, filter = request_params(request)
    #print "Params:", mol_type, filter
    # Now handle the POST content 
    libm = LibMethods(screen_lib, mol_type)
    my_mols = CloseableQueue.CloseableQueue()
    libm.get_mols(my_mols)
    results = process_pains(my_mols, filter)
   
    return generate_output(results)

