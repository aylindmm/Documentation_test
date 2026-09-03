import ast
import time
import pandas as pd
import pubchempy as pcp
from tqdm import tqdm

def _backoff_sleep(attempt):
    """Sleep for an exponentially increasing amount of time based on the number of failed attempts."""
    backoff_base=2
    wait = backoff_base ** attempt
    time.sleep(wait)
    return wait


def fetch_compound_info(df: pd.DataFrame, 
                        columns: list) -> pd.DataFrame:
    """
    Fetch compound information from PubChem for each compound listed in the specified columns of the DataFrame

    Arguments:
    df: pd.DataFrame - A DataFrame containing articles with 'DOI', 'PMID', and compound columns.
    columns: list - A list of column names in the DataFrame that contain compound names to be searched in PubChem.

    Returns:
    pd.DataFrame: A DataFrame containing metadata from the retrieved compounds.
    """

    delay=0.5
    max_retries=3
   
    compound_data = []
    processed_count = 0

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing compounds"):
        for column in columns:
            raw_value = row[column]

            # --- STEP 1: FIX THE DATA TYPE ---
            # This ensures we aren't iterating over letters in a string
            if isinstance(raw_value, str):
                if raw_value.startswith('['):
                    try:
                        compounds = ast.literal_eval(raw_value)
                    except:
                        compounds = [raw_value]
                else:
                    compounds = [raw_value]
            elif isinstance(raw_value, list):
                compounds = raw_value
            else:
                continue

            # --- STEP 2: SEARCH COMPOUNDS ---
            for compound in compounds:
                # Clean the string and skip noise
                compound = str(compound).strip()
                if not compound or compound in ["[", "]", ""]:
                    continue

                results = None
                success = False
                retries = max_retries

                while retries > 0 and not success:
                    try:
                        time.sleep(delay)
                        results = pcp.get_cids(compound, 'name', listkey_count=1, list_return='flat')
                        success = True
                    except Exception as e:
                        retries -= 1
                        attempt = max_retries - retries
                        wait = _backoff_sleep(attempt)
                        print(f"\nConnection error for {compound}: {e}, retrying in {wait}s... ({retries} left)")

                processed_count += 1

                if not success:
                    print(f"Failed search: {compound}" )
                else:

                    try:
                        # Fetch details for the first CID found
                        c = pcp.Compound.from_cid(results[0])
                        info = c.to_dict(properties=['smiles', 'iupac_name', 'inchikey', 'synonyms', 'cid'])
                        props = pcp.get_properties('Title', c.cid)
                        name = props[0]['Title'] 

                        # Safely handle synonyms
                        syns = info.get('synonyms', [])

                        compound_data.append({
                            "PMID": row.get('PMID'),
                            "DOI": row.get('DOI'),
                            "PubChem_CID": info.get('cid'),
                            "iupac_name": info.get('iupac_name'),
                            "inchi_key": info.get('inchikey'),
                            "name": name,
                            "synonyms": syns,
                            "smiles": info.get('smiles'),
                            "variable": column
                        })
                    except Exception as e:
                        print(f"No results for: {compound}")               

    print("\nCompound information retrieval complete.")
    print(f"\nTotal entries processed: {processed_count}")

    return pd.DataFrame(compound_data)
