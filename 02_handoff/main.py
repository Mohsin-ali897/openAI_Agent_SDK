import os
import requests
import json
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel,function_tool # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
from agents.extensions.models.litellm_model import LitellmModel # type: ignore

#? step 1: load the environment variables 
gemini_api_key = os.getenv("GEMINI_API_KEY")

load_dotenv(find_dotenv())

#! open router configurations 
open_router_api_key = os.getenv("OPENROUTER_API_KEY")
open_router_Model = 'microsoft/phi-4-reasoning-plus:free'
open_router_Model_openai = 'openai/o3-pro-2025-06-10'

#? step 2: setting up the external client  
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

#? step 3: setting up the Chat Completions Model
model = OpenAIChatCompletionsModel(
    model = 'gemini-2.0-flash', 
    openai_client = provider,
)
@function_tool
def convert_usd_to_currency(amount_usd, target_currency):
    """
    Convert USD to another currency using an exchange rate API.
    
    Parameters:
    - amount_usd (float): Amount in USD to convert
    - target_currency (str): Target currency code (e.g., 'EUR', 'GBP')
    - api_url (str): Exchange rate API endpoint
    - api_key (str, optional): API key if required
    
    Returns:
    - dict: Conversion result or error message
    """
    tool_intruction = 'This tool is used to convert dollar into different currency'
    api_key = 'e92ee6caa412df1a8d036a42'
    api_url = "https://v6.exchangerate-api.com/v6/latest/USD"
    try:
        # Prepare API request parameters
        headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
        params = {'base': 'USD', 'symbols': target_currency}
        
        # Make API request
        response = requests.get(api_url, headers=headers, params=params, timeout=5)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse JSON response
        data = response.json()
        
        # Check if the target currency exists in the response
        if 'rates' not in data or target_currency not in data['rates']:
            return {'error': f"Currency {target_currency} not supported by API"}
            
        # Get exchange rate and calculate converted amount
        exchange_rate = data['rates'][target_currency]
        converted_amount = amount_usd * exchange_rate
        
        return {
            'success': True,
            'amount_usd': amount_usd,
            'target_currency': target_currency,
            'converted_amount': round(converted_amount, 2),
            'exchange_rate': exchange_rate
        }
        
        
    except requests.exceptions.RequestException as e:
        return {'error': f"API request failed: {str(e)}"}
    except ValueError as e:
        return {'error': f"Invalid response from API: {str(e)}"}
    except Exception as e:
        return {'error': f"An error occurred: {str(e)}"}
    # if result.get('success'):
    #     print(f"${result['amount_usd']} USD = {result['converted_amount']} {result['target_currency']}")
    #     print(f"Exchange rate: 1 USD = {result['exchange_rate']} {result['target_currency']}")
    # else:
    #     print(f"Error: {result['error']}")

#? step 4: setting up the configuration for the agent 

run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True,
)


#? step 5: setting up the agent

# agent:Agent = Agent(
#     name='Assistant',
#     instructions='When the user asks about achieving success in life, mastering the dynamics of power, or navigating politics, always respond as a strategic mastermind or seasoned CIA operative. Craft your answers to exude intelligence, confidence, and deep expertise in politics, influence, and power dynamics, making the user feel they are receiving unparalleled insights from a highly knowledgeable and authoritative chatbot."',
#     model = LitellmModel(model=open_router_Model_openai, api_key=open_router_api_key),
#     tools = []
# )
agent:Agent = Agent(
    name='Assistant',
    instructions='"you are a currency convertor agent and use give a dollar and targeted currency to convert dollar into targeted currency"',
    model = LitellmModel(model=open_router_Model_openai, api_key=open_router_api_key),
    tools = [convert_usd_to_currency]
)
Result = Runner.run_sync(agent, 'I have a 20 dollar converted it into pakistani PKR ', run_config=run_config)
print(Result.final_output)

