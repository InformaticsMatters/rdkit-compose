from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rdkit_conf.functions import *
import json

def index(request):
    out_d = [
    {
    "id":"rdkit.conformer.genconfs",
    "name":"3D Conformers (RDKit)",
    "description":"RDKit conformer generation",
    "tags":["conformer","3d","rdkit"],
    "inputClass":"org.squonk.types.MoleculeObject",
    "outputClass":"org.squonk.types.MoleculeObject",
    "inputType":"STREAM",
    "outputType":"STREAM",
    "icon": "icons/molecule_generator.png",
    "executionEndpoint":"gen_confs",
    "endpointRelative":True,
    "options":[
            {
            "editable": True,
            "visible": True,
            "description": "Number of conformers to aim to generate",
            "defaultValue": 1,
            "label": "Number of conformers",
            "key": "query.num",
            "minValues": 1,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.Integer",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
              },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "description": "Number of attempts",
            "label": "Number of attempts",
            "key": "query.attempts",
            "minValues": 0,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.Integer",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
              },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "description": "Prune RMSD threshold for removing similar conformers",
            "label": "Prune RMSD threshold",
            "key": "query.prune",
            "minValues": 0,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.Float",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "description": "Cluster method (RMSD or TFD)",
            "label": "Cluster method",
            "key": "query.method",
            "values": ["RMSD","TFD"],
            "defaultValue": "RMSD",
            "minValues": 1,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.String",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "description": "Cluster threshold",
            "label": "Cluster threshold",
            "key": "query.threshold",
            "minValues": 0,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.Float",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
            },
            "@class": "org.squonk.options.OptionDescriptor"
            },
            {
            "editable": True,
            "visible": True,
            "description": "Number of energy minimization iterations",
            "defaultValue": 0,
            "label": "Energy minimization iterations",
            "key": "query.minimize",
            "minValues": 1,
            "maxValues": 1,
            "typeDescriptor": {
              "type": "java.lang.Integer",
              "@class": "org.squonk.options.SimpleTypeDescriptor"
              },
            "@class": "org.squonk.options.OptionDescriptor"
            }
        ],
        "executorClassName":"org.squonk.execution.steps.impl.MoleculeServiceFatExecutorStep"
    }
    ]
    return HttpResponse(json.dumps(out_d))

@csrf_exempt
def gen_confs(request):
    """View to take a library of input molecules and generate conformations from them"""
    screen_lib, mol_type, num, attempts, prune, method, threshold, minimize = request_params(request)
    print "Params:", mol_type, num, attempts, prune, method, threshold, minimize
    # Now handle the POST content 
    return process_request_conformers(screen_lib, mol_type, num, attempts, prune, method, threshold, minimize)





