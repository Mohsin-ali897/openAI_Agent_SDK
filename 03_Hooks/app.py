import requests # type: ignore
from typing import List, Dict, Optional

def google_search(query: str, num_results: int = 5) -> Dict:
    """
    Perform a search using Google Custom Search JSON API and return structured results.
    
    Args:
        query (str): The search query string.
        api_key (str): Google API key for Custom Search.
        cx (str): Custom Search Engine ID.
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
    
result = google_search('who is Rajab butt')
for i in result:
    print(f'key {result}  value is {result[i]} ')
    print('__'*10)
# print(result)