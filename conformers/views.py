from django.shortcuts import render
import urllib
from django.http import HttpResponse
from rdkit import Chem
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page
from json_function.json_parse import remove_keys
import ast
import urllib2
from mol_parsing.functions import process_input
from conf_gen.functions import *
from rdkit_screen.functions import LibMethods
from conf_gen.tasks import *


@csrf_exempt
def gen_confs(request):
    """View to take a library of input molecules and generate conformations from them"""
    screen_lib, mol_type, num, attempts, prune, method, threshold, minimize = request_handler(request)
    print "Params:", mol_type, num, attempts, prune, method, threshold, minimize
    # Now handle this file upload 
    libm = LibMethods(screen_lib, mol_type)
    my_mols = libm.get_mols()
    
    #return HttpResponse(json.dumps(ast.literal_eval(str((conf)))), content_type='application/json')
    return HttpResponse("OK Dude!")





