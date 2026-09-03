Usage
========================

This page walks through a typical aTUNApy workflow: searching PubMed for
articles, extracting text, retrieving compound information from PubChem, and
curating SMILES strings.

Installation
------------------------

.. code-block:: bash

   pip install atunapy


Before start
------------------------

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
For OpenAI, you can get your API key by signing up at https://openai.com/es-419/api/

For Groq, you can obtain your API token by signing up at https://console.groq.com/home

For Gemini, you can get your API key by signing up at https://aistudio.google.com/api-keys

For Anthropic, you can obtain your API key by signing up at https://platform.claude.com/docs/en/get-api-key

Important: Please ensure that you keep your API keys secure and do not share them publicly.

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

   NCBI E-utilities apply rate limits. Providing an API key and an e-mail
   address is recommended for large queries.

Step 2 — Extract text
---------------------

:mod:`atunapy.TextExtract` retrieves and cleans the text of the articles
found in the previous step.

.. code-block:: python

   # TODO: TextExtract example from the notebook

Step 3 — Query PubChem
----------------------

:mod:`atunapy.PubChemSearcher` looks up compound names mentioned in the text
and returns PubChem records (CID, IUPAC name, SMILES, ...).

.. code-block:: python

   # TODO: PubChemSearcher example from the notebook

Step 4 — Curate SMILES
----------------------

:mod:`atunapy.SMILEScuration` standardises and validates the SMILES strings
obtained from PubChem.

.. code-block:: python

   # TODO: SMILEScuration example from the notebook

Expected output
---------------

.. code-block:: text

   # TODO: paste a short sample of the resulting table / DataFrame

Next steps
----------

See the :doc:`api` for the full list of functions and parameters in each
module.