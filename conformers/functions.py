from rdkit import Chem
from rdkit.Chem import AllChem
from mol_parsing.functions import find_lib_type
from django.core.exceptions import ValidationError


def request_params(request):
    """Function to handle the request parameters"""
    screen_lib, mol_type = find_lib_type(request)
    if "num" in request.GET:
        num = request.GET["num"]
    else:
        num = 1
    if "attempts" in request.GET:
        attempts = request.GET["attempts"]
    else:
        attempts = 1
    if "prune" in request.GET:
        prune = request.GET["prune"]
    else:
        prune = 0.1
    if "method" in request.GET:
        method = request.GET["method"]
    else:
        method = "RMSD"
    if "threshold" in request.GET:
        threshold = request.GET["threshold"]
    else:
        if method == "TFD":
        	threshold = 0.3
        else:
        	threshold = 2.0
    if "minimize" in request.GET:
        minimize = request.GET["minimize"]
    else:
        minimize = 0
    return screen_lib, mol_type, num, attempts, prune, method, threshold, minimize

