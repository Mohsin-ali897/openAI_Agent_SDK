import os
import requests  # type: ignore
import json
from typing import List, Dict, Optional
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel,function_tool,enable_verbose_stdout_logging, ItemHelpers # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
from agents.extensions.models.litellm_model import LitellmModel # type: ignore
#* for streaming  
import asyncio
from openai.types.responses import ResponseTextDeltaEvent

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

search_agent_system_prompt = '''
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

async def main():
    Search_agent:Agent = Agent(
    name='Search_agent',
    instructions=search_agent_system_prompt,
    model= LitellmModel(model=open_router_Model_openai4o_min, api_key=open_router_api_key),
    tools = [google_search]
    )
    result = Runner.run_streamed(Search_agent, input="who is the president of pakistan and give me some introduction to him", run_config=run_config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            # print(event.data.delta, end="", flush=True)
            print(event)
    # async for event in result.stream_events():
    #     # We'll ignore the raw responses event deltas
    #     if event.type == "raw_response_event":
    #         continue
    #     elif event.type == "agent_updated_stream_event":
    #         print(f"Agent updated: {event.new_agent.name}")
    #         continue
    #     elif event.type == "run_item_stream_event":
    #         if event.item.type == "tool_call_item":
    #             print("-- Tool was called")
    #         elif event.item.type == "tool_call_output_item":
    #             print(f"-- Tool output: {event.item.output}")
    #         elif event.item.type == "message_output_item":
    #             print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}") # type: ignore
    #         else:
    #             pass  # Ignore other event types


asyncio.run(main())
    