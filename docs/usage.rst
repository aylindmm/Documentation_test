Usage
========================

This page walks through a typical aTUNApy workflow: searching PubMed for
articles, extracting text, retrieving compound information from PubChem, and
curating SMILES strings.

Before start
------------------------
.. note::
   Please ensure that you keep your API keys secure and do not share them publicly.

.. code-block:: python

   from atunapy import PubMedSearcher, PubChemSearcher, TextExtract, SMILEScuration

To use any of the LLMs supported by aTUNApy, you will need to provide your own API keys. You can set them as environment variables in your terminal:

.. code-block:: bash

   export OPENAI_API_KEY="your_openai_api_key"
   export GROQ_API_TOKEN="your_groq_api_token"
   export ANTHROPIC_API_KEY="your_anthropic_api_key"
   export GEMINI_API_KEY="your_gemini_api_key"

or you can also save them into an .env file in the root directory of your project:

.. code-block:: bash

    OPENAI_API_KEY=your_openai_api_key
    GROQ_API_TOKEN=your_groq_api_token
    ANTHROPIC_API_KEY=your_anthropic_api_key
    GEMINI_API_KEY=your_gemini_api_key


for this to work, you will need to install the python-dotenv package:

.. code-block:: bash

   pip install python-dotenv    

and then load the .env file in your script:


.. code-block:: python

    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file


How to get API keys
------------------------

You can get your API key by signing up at the following links:

OpenAI: https://openai.com/es-419/api/

Groq: https://console.groq.com/home

Gemini: https://aistudio.google.com/api-keys

Anthropic: https://platform.claude.com/docs/en/get-api-key


.. note::
   Take into consideration that some of the LLMs have usage limits or costs associated with their usage, so be sure to review the terms and conditions of each provider.


Step 1 — Search PubMed
------------------------

Use :mod:`atunapy.PubMedSearcher` to query PubMed and collect article
identifiers and metadata.

.. code-block:: python

    articles = PubMedSearcher.fetch_articles(search_terms = ['ototoxicity', 'hearing loss', '(inner ear) AND (drug induced damage)'],
                                                email = os.environ.get('EMAIL_ADDRESS'),
                                                api_key = os.environ.get('NCBI_API_KEY'))

.. note::

   NCBI E-utilities do not required an API key or email, however they apply rate limits. Providing an API key and an e-mail address is recommended for large queries.

Step 2 — Extract text
---------------------

:mod:`atunapy.TextExtract` retrieves and cleans the text of the articles
found in the previous step.

To run a text query you will need to provide a prompt that describes the task you want the LLM to perform. The best results are obtained when the prompt is clear and specific. 

You also need to provide a list of variables that will be extracted by the LLM. An example of such df is shown below. 

.. code-block:: python
   df = pd.DataFrame({
    'Name': ['ototoxic drugs', 'otoprotective drugs', 'effects', 'mechanism of ototoxicity'],
    'Description': ["Any ototoxic drugs or molecules", 
                    "Any drugs or molecules mentioned as protective against ototoxicity or used to treat drug-induced hearing loss.", 
                    'Clasify the ototoxicity as "Cochleo-toxicity", "Vestibulo-toxicity", "Dizzines", "not mentioned" or "Other"', 
                    "Note the described mechanism for the ototoxic compounds  mentioned (e.g., cochlear hair cell damage, vasoconstriction). Give a very short answer."],
    'Type': ["List", "List", "String", "String"]
    })


To define the prompt, you can use the following template. You can modify it to suit your specific needs:

.. code-block:: python

   tool = TextExtract.LLMTextExtractor(
                 prompt = """You are an expert pharmacologist specializing in otolaryngology. 
                  Your task is to extract drug information from the following research article.

                  Definitions:
                  - Ototoxic Agent: A drug or molecule that causes damage to the inner ear (cochleotoxicity or vestibulotoxicity), hearing loss or dizziness.
                  - Otoprotective Agent: A compound that prevents or mitigates such damage.

                  Instructions:
                  1. Identify all drugs, molecules, or experimental compounds mentioned.
                  2. Determine their role: "Ototoxic" or "Otoprotective".
                  """,
                 variables = df
                 )


Once you have defined the prompt and variables, you can run the text extraction process on the articles retrieved from PubMed. 

.. code-block:: python

   results = tool.process_articles(df = articles[:10], # Test with a small subset of articles first, once you are satisfied with the results, you can process the entire dataset.
                                    LLM = "Gemini",
                                    api_key = os.environ.get('GEMINI_KEY'), 
                                    model = "gemini-3.5-flash-lite",)   
   print("Claude extraction complete.")


.. note::
   To avoid exceeding usage limits, it is recommended to test with a small subset of articles first, once you are satisfied with the results, you can process the entire dataset.


Step 3 — Query PubChem
----------------------

:mod:`atunapy.PubChemSearcher` looks up compound names mentioned in the text
and returns PubChem records (CID, IUPAC name, SMILES, InChIKey and synonyms).

.. code-block:: python
   compounds = PubChemSearcher.fetch_compound_info(df=results,
                                            columns=["ototoxic_drugs", "otoprotective_drugs"] # List with the names of the columns in the results DataFrame that contain the compound names to be queried in PubChem
                                            )


Step 4 — Curate SMILES
----------------------

:mod:`atunapy.SMILEScuration` standardises and validates the SMILES strings
obtained from PubChem.

.. code-block:: python

   compounds["Clean_SMILES"] = [SMILEScuration.standardize(x) for x in compounds["smiles"]]


Next steps
----------

See the :doc:`api` for the full list of functions and parameters in each
module.