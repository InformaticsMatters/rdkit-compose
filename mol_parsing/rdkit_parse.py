#Series of functions to parse molecules based on RDKit
import sys
from rdkit import Chem
from sanifix import fix_mol
from ijson import items


def parse_mol_simple(my_type, txt):
    """Function to parse individual mols given a type"""
    if my_type == "mol":
        # Try this way
        mol = Chem.MolFromMolBlock(txt.strip())
        if mol is None:
            mol = Chem.MolFromMolBlock(txt)
        if mol is None:
            mol = Chem.MolFromMolBlock("\n".join(txt.split("\n")[1:]))
        # Now try to do sanidfix
        if mol is None:
            mol = fix_mol(Chem.MolFromMolBlock(txt, False))
        # Annd again
        if mol is None:
            mol = fix_mol(Chem.MolFromMolBlock(txt.strip(), False))
    elif my_type == "smiles":
        # Assumes that smiles is the first column -> and splits on chemaxon
        mol = Chem.MolFromSmiles(txt.split()[0].split(":")[0])
    elif my_type == "inchi":
        # Assumes that INCHI is the first column
        mol = Chem.MolFromInchi(my_txt.split()[0], my_vals)
    if mol is None:
        print txt
    return mol


def parse_mol_json(molobj):
    """Function to get the RDKit mol from MoleculeObject JSON"""
    #print "reading mol",molobj["uuid"],molobj["format"]
    molstr = str(molobj["source"])
    # Get the format and use this as a starting point to work out 
    molformat = molobj["format"]
    # Now parse it with RDKit
    mol = parse_mol_simple(molformat, molstr)
    mol.SetProp("uuid", str(molobj["uuid"]))
    return mol
   

def generate_mols_from_json(json):
	j=0
	for item in items(json, "item"):
		j+=1
		#print "  reading",j
		mol = parse_mol_json(item)
		yield mol


