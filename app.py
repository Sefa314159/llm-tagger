from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_pydantic_to_openai_function
from pydantic import BaseModel, Field
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Default environment variables
DEFAULT_OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
DEFAULT_OPENAI_MODEL_NAME = os.environ.get('OPEN_AI_MODEL_NAME', 'gpt-4o-mini')
DEFAULT_OPENAI_MODEL_TEMPERATURE = float(os.environ.get('OPENAI_MODEL_TEMPERATURE', 0.0))


class Tagging(BaseModel):
    """
    A model for tagging and analyzing text with sentiment, language, and intent.
    
    This class provides a structured way to categorize text inputs based on their
    emotional tone, language, and the underlying purpose or intention of the message.
    """
    sentiment: str = Field(
        description="Sentiment of the text; expected values: `positive`, `negative`, `neutral` or `mixed` (positive and negative)."
    )
    language: str = Field(
        description="Language of the text in ISO 639-1 format."
    )
    intent: str = Field(
        description="""
        Intent of the text; examples include: 
        `inquiry`, `purchase_intention`, `complaint`, `greeting`, 
        `package_change`, `renewal`, `feedback`, `information_request`, 
        `technical_support`, `account_management`, `cancellation`, 
        `general_question`, `suggestion`, `appreciation`, `urgent_request`,
        `confirmation`, `refund_request`, `pricing_inquiry`, `subscription_change`,
        `product_comparison`, `status_check`, `troubleshooting`, `feature_request`,
        `bug_report`, `scheduling`, `appointment_setting`, `order_tracking`,
        `return_request`, `warranty_claim`, `delivery_issue`, `invoice_query`,
        `payment_problem`, `recommendation_request`, `partnership_proposal`,
        `job_application`, `service_upgrade`, `service_downgrade`, `promotional_inquiry`,
        `password_reset`, `login_issue`, `notification_preferences`, `data_privacy`,
        `account_verification`, `security_concern`, `training_request`, `demo_request`,
        `marketing_inquiry`, `sales_inquiry`, `referral`, `discount_request`.
        """.strip()
    )


class LLMTagger():
    """
    A class that uses a language model to analyze and tag text.
    
    This class leverages OpenAI's language models to detect sentiment, language,
    and intent in text inputs, using the Tagging schema for structured output.
    """
    def __init__(self, api_key=None, model_name=None, temperature=None):
        """
        Initialize the LLMTagger with the configured language model and processing chain.
        
        Sets up the ChatOpenAI model with environment variables, configures function calling
        for structured output, and establishes the processing pipeline.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, uses the environment variable.
            model_name (str, optional): OpenAI model name. If None, uses the environment variable.
            temperature (float, optional): Model temperature. If None, uses the environment variable.
        """
        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', DEFAULT_OPENAI_API_KEY)
        self.model_name = model_name or os.environ.get('OPEN_AI_MODEL_NAME', DEFAULT_OPENAI_MODEL_NAME)
        
        # Ensure temperature is a float
        temp_str = os.environ.get('OPENAI_MODEL_TEMPERATURE', str(DEFAULT_OPENAI_MODEL_TEMPERATURE))
        self.temperature = temperature if temperature is not None else float(temp_str)
        
        # Initialize the model with the provided or default settings
        model = ChatOpenAI(
            temperature=self.temperature,
            model=self.model_name,
            api_key=self.api_key
        )
        
        tagging_functions = [convert_pydantic_to_openai_function(Tagging)]
        model_with_functions = model.bind(functions=tagging_functions, function_call={"name": "Tagging"})
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Think carefully, and then tag the text as instructed"),
            ("user", "{input}")
        ])
        
        self.tagging_chain = prompt | model_with_functions | JsonOutputFunctionsParser()
    
    def tag(self, text: str) -> dict:
        """
        Analyze and tag the provided text.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: A dictionary containing the sentiment, language, and intent analysis.
        """
        return self.tagging_chain.invoke({"input": text})