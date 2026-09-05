<img width="760" height="576" alt="image" src="https://github.com/user-attachments/assets/e21d3dbd-0234-4c08-9dcd-4c5bf2de6316" />


A Python toolkit for mining the biomedical literature: search PubMed for articles, extract structured information from their text with an LLM, look up the compounds mentioned in PubChem, and curate the resulting SMILES strings.

## Table of contents

- [Installation](#installation)
- [Setup](#setup)
  - [API keys](#api-keys)
  - [Where to get API keys](#where-to-get-api-keys)
- [Usage](#usage)
  - [Step 1 — Search PubMed](#step-1--search-pubmed)
  - [Step 2 — Extract text](#step-2--extract-text)
  - [Step 3 — Query PubChem](#step-3--query-pubchem)
  - [Step 4 — Curate SMILES](#step-4--curate-smiles)
- [Next steps](#next-steps)

## Installation

It is recommended to create a virtual environment first:

```bash
conda create --name atunapy_new "python>=3.8" pip
conda activate atunapy_new
```

Install from PyPI:

```bash
pip install atunapy
```

Or install from source:

```bash
git clone https://github.com/aylindmm/aTUNApy.git
cd aTUNApy
pip install -e .
```

## Setup

```python
from atunapy import PubMedSearcher, PubChemSearcher, TextExtract, SMILEScuration
```

### API keys

To use any of the LLMs supported by aTUNApy you need to provide your own API keys. You can set them as environment variables in your terminal:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export GROQ_API_TOKEN="your_groq_api_token"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

Or save them in a `.env` file in the root directory of your project:

```
OPENAI_API_KEY=your_openai_api_key
GROQ_API_TOKEN=your_groq_api_token
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
```

For the `.env` approach, install `python-dotenv`:

```bash
pip install python-dotenv
```

and load the file at the top of your script:

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
```

> **Note:** Keep your API keys secure and never share them publicly or commit them to version control.

### Where to get API keys

| Provider  | Link |
|-----------|------|
| OpenAI    | https://openai.com/es-419/api/ |
| Groq      | https://console.groq.com/home |
| Gemini    | https://aistudio.google.com/api-keys |
| Anthropic | https://platform.claude.com/docs/en/get-api-key |

> **Note:** Some LLM providers have usage limits or costs associated with their APIs. Be sure to review the terms and conditions of each provider.

## Usage

A typical aTUNApy workflow has four steps: search PubMed, extract text with an LLM, retrieve compound information from PubChem, and curate the SMILES strings.

```python
import os
import pandas as pd
from atunapy import PubMedSearcher, PubChemSearcher, TextExtract, SMILEScuration
```

### Step 1 — Search PubMed

Use `atunapy.PubMedSearcher` to query PubMed and collect article identifiers and metadata.

```python
articles = PubMedSearcher.fetch_articles(
    search_terms=['ototoxicity', 'hearing loss', '(inner ear) AND (drug induced damage)'],
    email=os.environ.get('EMAIL_ADDRESS'),
    api_key=os.environ.get('NCBI_API_KEY'),
)
```

> **Note:** NCBI E-utilities do not require an API key or email address, but they do apply rate limits. Providing both is recommended for large queries.

### Step 2 — Extract text

`atunapy.TextExtract` retrieves and cleans the text of the articles found in the previous step, then uses an LLM to extract the information you ask for.

You need two things: a **prompt** describing the task (clear, specific prompts give the best results) and a **DataFrame of variables** to extract. Each variable has a name, a description, and a type (`"List"` or `"String"`):

```python
df = pd.DataFrame({
    'Name': ['ototoxic drugs', 'otoprotective drugs', 'effects', 'mechanism of ototoxicity'],
    'Description': [
        "Any ototoxic drugs or molecules",
        "Any drugs or molecules mentioned as protective against ototoxicity or used to treat drug-induced hearing loss.",
        'Classify the ototoxicity as "Cochleo-toxicity", "Vestibulo-toxicity", "Dizziness", "not mentioned" or "Other"',
        "Note the described mechanism for the ototoxic compounds mentioned (e.g., cochlear hair cell damage, vasoconstriction). Give a very short answer.",
    ],
    'Type': ["List", "List", "String", "String"],
})
```

Define the extractor with a prompt. The template below can be adapted to your needs:

```python
tool = TextExtract.LLMTextExtractor(
    prompt="""You are an expert pharmacologist specializing in otolaryngology.
    Your task is to extract drug information from the following research article.

    Definitions:
    - Ototoxic Agent: A drug or molecule that causes damage to the inner ear (cochleotoxicity or vestibulotoxicity), hearing loss or dizziness.
    - Otoprotective Agent: A compound that prevents or mitigates such damage.

    Instructions:
    1. Identify all drugs, molecules, or experimental compounds mentioned.
    2. Determine their role: "Ototoxic" or "Otoprotective".
    """,
    variables=df,
)
```

Then run the extraction on the articles retrieved from PubMed:

```python
results = tool.process_articles(
    df=articles[:10],  # Test with a small subset first
    LLM="Gemini",
    api_key=os.environ.get('GEMINI_API_KEY'),
    model="gemini-3.5-flash-lite",
)
print("Extraction complete.")
```

> **Note:** To avoid exceeding usage limits, test with a small subset of articles first. Once you are satisfied with the results, process the entire dataset.

### Step 3 — Query PubChem

`atunapy.PubChemSearcher` looks up the compound names found in the text and returns PubChem records (CID, IUPAC name, SMILES, InChIKey and synonyms).

```python
compounds = PubChemSearcher.fetch_compound_info(
    df=results,
    columns=["ototoxic_drugs", "otoprotective_drugs"],  # columns of `results` containing compound names
)
```

### Step 4 — Curate SMILES

`atunapy.SMILEScuration` standardises and validates the SMILES strings obtained from PubChem.

```python
compounds["Clean_SMILES"] = [SMILEScuration.standardize(x) for x in compounds["smiles"]]
```

## Next steps

See the API documentation for the full list of functions and parameters in each module.
