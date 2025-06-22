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
open_router_Model_openai4o_min = 'openai/gpt-4o-mini'

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
    It is a fuction use to Convert USD to another currency using an exchange rate API.
    
    Parameters:
    - amount_usd (float): Amount in USD to convert
    - target_currency (str): Target currency code (e.g., 'EUR', 'GBP') it get abbreviated of a currency
    Returns:
    - dict: Conversion result or error message
    """
    tool_intruction = 'This tool is used to convert dollar into different currency'
    api_key = 'e92ee6caa412df1a8d036a42'
    api_url = "https://v6.exchangerate-api.com/v6/e92ee6caa412df1a8d036a42/latest/USD"
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
        if 'conversion_rates' not in data or target_currency not in data['conversion_rates']:
            return {'error': f"Currency {target_currency} not supported by API"}
            
        # Get exchange rate and calculate converted amount
        exchange_rate = data['conversion_rates'][target_currency]
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
    
@function_tool

def get_weather(location):
    """
    Fetch current weather information for a specific location using WeatherAPI.
    
    Args:
        location (str): City name, e.g., 'London' or 'New York,US ',passed by value in param['q']
    
    Returns:
        dict: Weather data if successful, None if failed
    """
    base_url = "http://api.weatherapi.com/v1"
    endpoint = "/current.json"
    
    # Parameters for the API request
    api_key='029f2c6f5d8e4ee5844163821252206'
    params = {
        'key': api_key,
        'q': location,
        'aqi': 'no'  # Exclude air quality data
    }
    
    try:
        # Make the API request
        response = requests.get(base_url + endpoint, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
    
            # Extract relevant weather information
            weather_info = {
                'location': f"{data['location']['name']}, {data['location']['country']}",
                'temperature_c': data['current']['temp_c'],
                'temperature_f': data['current']['temp_f'],
                'condition': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'wind_kph': data['current']['wind_kph'],
                'last_updated': data['current']['last_updated']
            }
            return weather_info
        else:
            print(f"Error: {response.status_code} - {response.json().get('error', {}).get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing response: Missing key {e}")
        return None


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
    instructions='"you are a currency convertor agent and use convert_usd_to_currency tools it take a two argument amount_usd and  target_currency pass a argument how much dollar and a targeted currency  convert dollar into targeted currency"',
    model = LitellmModel(model=open_router_Model_openai4o_min, api_key=open_router_api_key),
    tools = [convert_usd_to_currency]
)
weather_agent:Agent = Agent(
    name='Assistant',
    instructions='"You are an Weather agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. Use get_weather tool it,s require one argument location to check the weather condition You MUST plan extensively before function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully."',
    model = LitellmModel(model=open_router_Model_openai4o_min, api_key=open_router_api_key),
    tools = [get_weather]
)
Result = Runner.run_sync(agent, 'I have a 20 dollar converted it into chinese currency ', run_config=run_config)
print(Result.final_output)
Result = Runner.run_sync(weather_agent, 'what about weather in karachi, pakistan.', run_config=run_config)
print(Result.final_output)
