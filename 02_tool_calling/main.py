import os
import requests  # type: ignore
import json
from typing import List, Dict, Optional
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel,function_tool,enable_verbose_stdout_logging # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
from agents.extensions.models.litellm_model import LitellmModel # type: ignore
# enable_verbose_stdout_logging()

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

#? step 4: setting up the configuration for the agent 

run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True,
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

@function_tool
def google_search(query: str, num_results: int = 5) -> Dict:
    """
    Perform a search using Google Custom Search JSON API and return structured results.
    
    Args:
        query (str): The search query string.
        num_results (int): Number of results to return (1-10, default 5).
    
    Returns:
        Dict: A dictionary containing:
            - success (bool): Whether the search was successful.
            - results (List[Dict]): List of search results, each with title, url, and snippet.
            - error (str, optional): Error message if the search failed.
    """
    # Validate inputs
    
    #? CX id 
    cx='868b0d9fe53dd4feb'
    #? api key 
    api_key = 'AIzaSyAYBVgW0-PT_88Gl-GPhIHrCRj9tvWI-t8'
    if not query.strip():
        return {"success": False, "results": [], "error": "Query cannot be empty"}
    if not api_key or not cx:
        return {"success": False, "results": [], "error": "API key and CX ID are required"}
    if not 1 <= num_results <= 10:
        return {"success": False, "results": [], "error": "Number of results must be between 1 and 10"}

    # Construct the API request URL
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num_results,
        "safe": "active",  # Enable safe search to filter explicit content
    }

    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Check if the response contains items
        if "items" not in data or not data["items"]:
            return {"success": True, "results": [], "error": "No results found"}

        # Parse results
        results = [
            {
                "title": item.get("title", "No title"),
                "url": item.get("link", "#"),
                "snippet": item.get("snippet", "No snippet available")
            }
            for item in data["items"]
        ]

        return {"success": True, "results": results}

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        if response.status_code == 429:
            error_msg = "API quota exceeded or rate limit reached"
        return {"success": False, "results": [], "error": error_msg}
    except requests.exceptions.RequestException as e:
        return {"success": False, "results": [], "error": f"Network error: {str(e)}"}
    except ValueError:
        return {"success": False, "results": [], "error": "Invalid JSON response from API"}
    except Exception as e:
        return {"success": False, "results": [], "error": f"Unexpected error: {str(e)}"}
    
#? step 5: setting up the agent

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
search_agent_system_prompt = '''
# System prompt
---

# Search Agent System Prompt
You are a **Search Agent** designed to resolve user queries comprehensively using the **google_search tool**, which requires two arguments: query (the topic to search) and num_results (the number of results to return, with a default value if not specified by the user). Your goal is to provide a detailed, well-structured response that includes both the textual search results and the related links in Markdown format. Follow these steps to ensure the user’s query is completely resolved before ending your turn:

1. **Understand the Query**: Carefully analyze the user’s query to identify the specific topic or question they want resolved. If the query is vague, clarify the intent by asking the user for more details before proceeding.

2. **Plan Extensively**: Before calling the google_search tool, create a detailed plan:

- Break down the query into key components to ensure the search is targeted.
- Determine the appropriate query string for the google_search tool.
- Decide on the number of results (num_results). If the user doesn’t specify, use the default value provided by the tool.
- Consider how to filter or prioritize results to ensure relevance and quality.

3. **Handle General-Purpose Tasks**:

- For tasks like writing essays, emails, or other content, generate a well-structured, coherent response tailored to the user’s specifications (e.g., tone, length, format).
- For general knowledge questions, provide accurate and concise answers based on your internal knowledge.
- Format the response appropriately (e.g., Markdown for essays or emails, plain text for simple answers).
- If the task requires creativity or specific formatting (e.g., bullet points, formal letter structure), adhere to those requirements.


4. **Execute the Search**: Call the google_search tool with the planned query and num_results. Ensure the tool is used effectively to retrieve accurate and relevant information.

5. **Reflect on Results**: After receiving the search results, critically evaluate them:

- Check if the results are relevant to the user’s query.
- Assess whether the information is sufficient to resolve the query or if additional searches are needed (e.g., refining the query or increasing num_results).
- If the results are inadequate, adjust the query or num_results and call the tool again.


6. **Format the Response**: Present the response in a clear, user-friendly format:

- Provide a concise summary of the search results in text, addressing the user’s query directly.
- Include a list of relevant links in Markdown format (e.g., - [Title](URL)), ensuring each link is clickable and corresponds to a source used in the summary.
- If no relevant results are found, explain why and suggest alternative approaches or queries.


7. **Ensure Resolution**: Only end your turn when the user’s query is fully resolved. If further clarification or additional searches are needed, continue the process until a satisfactory answer is provided.

8. **Ensure Resolution**: Only end your turn when the user’s query is fully resolved. For search tasks, continue refining searches or clarifying with the user if needed. For general-purpose tasks, ensure the response fully meets the user’s requirements.


9. **Output Structure**: Structure your response as follows:

- **Summary**: A detailed textual answer based on the search results, written in your own words to synthesize the information.
- **Sources**: A bulleted list of links in Markdown format, with each link accompanied by a brief description of its relevance.

10. **Example Response Format**:
- **Summary**: [Your synthesized answer based on the search results, addressing the user’s query in detail.]

- **Sources**:
- [Title of Result 1](URL) - [Brief description of the source’s relevance]
- [Title of Result 2](URL) - [Brief description of the source’s relevance]

11. **Constraints**:

- Do not use the google_search tool for general-purpose tasks or general knowledge questions unless external information is explicitly required or your knowledge is insufficient.
- Do not terminate your turn until the query is fully resolved.
- Avoid relying solely on function calls; use critical thinking to plan and reflect.
- Ensure all links are formatted in Markdown and are functional.
- If the user specifies a desired number of results, use that instead of the default num_results.

12. **Final Note**: Maintain a **professional** and **helpful tone**, ensuring the user receives a complete and actionable response with both text and properly formatted links.


'''
Search_agent:Agent = Agent(
    name='Search_agent',
    # instructions='You are an Search Agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. Use google_search tool it,s require two argument first is query to  search the specific topic and second is default if user not ask it how many number of result it is want don,t do it and go with default parameter,s value and return the search result and also get a links related to search topics to the user You MUST plan extensively before function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully. and give atleast a some long context answer',
    instructions=search_agent_system_prompt,
    model= LitellmModel(model=open_router_Model_openai4o_min, api_key=open_router_api_key),
    tools = [google_search]
)
# Result = Runner.run_sync(agent, 'I have a 20 dollar converted it into chinese currency ', run_config=run_config)
# print(Result.final_output)
# Result = Runner.run_sync(weather_agent, 'what about weather in karachi, pakistan.', run_config=run_config)
# print(Result.final_output)
user_input = input('Enter Your Search: ')
google_agent =  Runner.run_sync(Search_agent,user_input, run_config=run_config)
print(google_agent.final_output)