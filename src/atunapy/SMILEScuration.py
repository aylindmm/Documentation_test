import pandas as pd
from rdkit import Chem
from rdkit.Chem.SaltRemover import SaltRemover
from rdkit.Chem.MolStandardize import rdMolStandardize

"""
This module provides a function to standardize SMILES strings by performing the following steps:
1. Strip salts (keeping the largest fragment)  
2. Neutralize charges
3. Canonicalize Tautomers
4. Generate Canonical SMILES string

Arguments:
    smiles (str): The SMILES string to be standardized.
Returns:
    str: The standardized SMILES string, or None if the input is invalid or cannot be processed.
"""
def standardize(smiles: str) -> str:
    if pd.isna(smiles) or str(smiles).strip() == "":
        return None
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None: return None

        # 1. Strip Salts (keeps the largest fragment)
        remover = SaltRemover()
        mol = remover.StripMol(mol, dontRemoveEverything=True)
        
        # 2. Neutralize Charges
        uncharger = rdMolStandardize.Uncharger()
        mol = uncharger.uncharge(mol)

        # 3. Canonicalize Tautomers
        te = rdMolStandardize.TautomerEnumerator()
        mol = te.Canonicalize(mol)

        # 4. Generate Canonical SMILES string
        return Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
    
    except:
        return None
