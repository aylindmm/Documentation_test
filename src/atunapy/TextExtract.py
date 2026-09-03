
import pandas as pd
import time
from tqdm import tqdm
from typing import List
from pydantic import Field, create_model, field_validator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class LLMTextExtractor:
    """Class to extract structured information from scientific abstracts using LLMs.

    Attributes:
        prompt (str): The instruction for the LLM to extract information.   
        variables (pd.DataFrame): A DataFrame containing the variables to extract, with columns 'Name', 'Description', and 'Type'.
        system_message (str): The system message for the LLM, providing context about the task.
    
    """
    def __init__(self, 
                 prompt: str, 
                 variables: pd.DataFrame, 
                 system_message: str = "You are a medicinal chemist that extracts information from scientific abstracts. Only retrieve the information requested if it is explicitly stated in the text provided. Do not infer or assume any information that is not directly mentioned."):
        self.prompt = prompt
        self.variables = variables
        self.system_message = system_message

    def define_dynamic_response_format(self):
        """Dynamically create a Pydantic model based on the provided variables DataFrame."""
        fields = {}
        list_fields = []
        for _, row in self.variables.iterrows():
            var_name = row['Name'].lower().replace(" ", "_").replace("-", "_")
            description = row['Description'].strip()
            vtype = row['Type'].strip().lower()

            if vtype == "list" or vtype == "List":
                fields[var_name] = (List[str], Field(default_factory=list, description=description))
                list_fields.append(var_name)
            else:
                fields[var_name] = (str, Field(default="", description=description))

        def _coerce_null_string( v):
            if isinstance(v, str):
                return [] if v.strip().lower() == "null" else [v]
            return v

        validators = {}
        if list_fields:
            validators["_coerce_null_lists"] = field_validator(*list_fields, mode="before")(_coerce_null_string)

        DynamicResponseFormat = create_model('DynamicResponseFormat', __validators__=validators, **fields)
        return DynamicResponseFormat

    
    def prompt_template(self):
        """Create a ChatPromptTemplate for the LLM based on the system message and user instruction."""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("user", """{instruction}
            
            Article title: "{art_title}"
            Article abstract: "{art_abstract}"
            
            Do NOT include in your responses escape characters like \', \n, or \".
            """)])
        return prompt_template
    
    # Fetch LLM data based on the specified model
        
    def fetch_gpt_data(self,
                       api_key: str,
                       model: str):
       
        llm = ChatOpenAI(model=model, 
                         temperature=0.0, 
                         openai_api_key=api_key).with_structured_output(self.define_dynamic_response_format())
        return llm
        
    def fetch_claude_data(self,
                       api_key: str,
                       model: str):
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(model=model, 
                    temperature=0.0, 
                    anthropic_api_key=api_key).with_structured_output(self.define_dynamic_response_format())
        return llm

    def fetch_llama_data(self,
                       api_key: str,
                       model: str):
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=model,
            temperature=0.0,
            api_key=api_key).with_structured_output(self.define_dynamic_response_format(), method="function_calling")
        return llm

    def fetch_gemini_data(self,
                       api_key: str,
                       model: str):
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model, 
                    temperature=0.0, 
                    google_api_key=api_key).with_structured_output(self.define_dynamic_response_format())
        return llm
    # Extract data from articles using the specified LLM and model

    def process_articles(self, 
                         LLM: str, 
                         df: pd.DataFrame, 
                         api_key: str = None, 
                         model: str = None) -> pd.DataFrame:
        """
        Process articles using the specified LLM and model, extracting structured information based on the prompt.

        Args:
            LLM (str): The name of the LLM to use. Options are 'GPT', 'Claude', 'LLaMA', or 'Gemini'.
            df (pd.DataFrame): A DataFrame containing articles with 'DOI', 'PMID', 'Title' and 'Abstract' columns.
            api_key (str): The API key for the specified LLM. Required for API access.
            model (str): The model to use for the specified LLM.
        Returns:
            pd.DataFrame: A DataFrame containing metadata from the retrieved articles.
        """

        start_time = time.perf_counter() # Start the timer
        
        if LLM == "GPT": 
            llm = self.fetch_gpt_data(api_key, model)
        elif LLM == "Claude":
            llm = self.fetch_claude_data(api_key, model)
        elif LLM == "LLaMA":
            llm = self.fetch_llama_data(api_key, model)
        elif LLM == "Gemini":
            llm = self.fetch_gemini_data(api_key, model)
        else:
            raise ValueError(f"Unsupported LLM: {LLM}. \
                             Please choose from 'GPT', 'Claude', 'LLaMA', or 'Gemini'.")
        
        
        prompt_template = self.prompt_template() # Create prommpt template
        chain = prompt_template | llm   
        print(f"Processing articles with {LLM}, model: {model}...")
        
        results = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing articles"):
            try:
                # invoke() handles the API call and the parsing automatically
                response = chain.invoke({
                    "instruction": self.prompt,
                    "art_title": row.get("Title", ""),
                    "art_abstract": row.get("Abstract", "")
                })
                # response is now a Pydantic object, we convert it to a dict
                response_data = response.model_dump()
                response_data["PMID"] = row.get("PMID")
                results.append(response_data)
                # wait for 2 seconds to avoid hitting rate limits
                if LLM in ["LLaMA", "Gemini"]:
                    time.sleep(2)  # Adjust sleep time as needed for rate limits
                
            except Exception as e:
                print(f"Error processing PMID {row.get('PMID')}: {e}")
                continue

        # build DataFrame once
        results = pd.DataFrame(results)
        print(f"{LLM} search executed in ", round(time.perf_counter() - start_time, 2), "seconds")
        return results
