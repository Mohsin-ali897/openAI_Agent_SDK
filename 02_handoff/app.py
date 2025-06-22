# # import requests
# # import json
# api_url= 'https://v6.exchangerate-api.com/v6/e92ee6caa412df1a8d036a42/latest/USD'
# # response = requests.get(api_url,timeout=5)
# # response.raise_for_status() 
# # print(response.json())
# import requests
# import json

# def convert_usd_to_currency(amount_usd, target_currency, api_url, api_key=None):
#     """
#     Convert USD to another currency using an exchange rate API.
    
#     Parameters:
#     - amount_usd (float): Amount in USD to convert
#     - target_currency (str): Target currency code (e.g., 'EUR', 'GBP')
#     - api_url (str): Exchange rate API endpoint
#     - api_key (str, optional): API key if required
    
#     Returns:
#     - dict: Conversion result or error message
#     """
#     try:
#         # Prepare API request parameters
#         headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
#         params = {'base': 'USD', 'symbols': target_currency}
        
#         # Make API request
#         response = requests.get(api_url, headers=headers, params=params, timeout=5)
#         response.raise_for_status()  # Raise exception for bad status codes
        
#         # Parse JSON response
#         data = response.json()
        
#         # Check if the target currency exists in the response
#         if 'rates' not in data or target_currency not in data['rates']:
#             return {'error': f"Currency {target_currency} not supported by API"}
            
#         # Get exchange rate and calculate converted amount
#         exchange_rate = data['rates'][target_currency]
#         converted_amount = amount_usd * exchange_rate
        
#         return {
#             'success': True,
#             'amount_usd': amount_usd,
#             'target_currency': target_currency,
#             'converted_amount': round(converted_amount, 2),
#             'exchange_rate': exchange_rate
#         }
        
#     except requests.exceptions.RequestException as e:
#         return {'error': f"API request failed: {str(e)}"}
#     except ValueError as e:
#         return {'error': f"Invalid response from API: {str(e)}"}
#     except Exception as e:
#         return {'error': f"An error occurred: {str(e)}"}

# # Example usage
# if __name__ == "__main__":
#     # Replace with your actual API endpoint and key
#     API_URL = "https://api.exchangerate-api.com/v4/latest/USD"  # Example API
#     API_URL = "https://v6.exchangerate-api.com/v6latest/USD"  # Example API
#     API_KEY = 'e92ee6caa412df1a8d036a42'  # Set to your API key if required
    
#     # Test the function
#     result = convert_usd_to_currency(100, "PKR", API_URL, API_KEY)
#     if result.get('success'):
#         print(f"${result['amount_usd']} USD = {result['converted_amount']} {result['target_currency']}")
#         print(f"Exchange rate: 1 USD = {result['exchange_rate']} {result['target_currency']}")
#     else:
#         print(f"Error: {result['error']}")
import requests

def get_weather(location):
    """
    Fetch current weather information for a specific location using WeatherAPI.
    
    Args:
        api_key (str): Your WeatherAPI key
        location (str): City name, e.g., 'London' or 'New York,US'
    
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
            print(data)
    
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

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    
    location = "London"
    
    weather = get_weather(location)
    
    # if weather:
    #     print(f"Weather in {weather['location']}:")
    #     print(f"Temperature: {weather['temperature_c']}°C ({weather['temperature_f']}°F)")
    #     print(f"Condition: {weather['condition']}")
    #     print(f"Humidity: {weather['humidity']}%")
    #     print(f"Wind Speed: {weather['wind_kph']} kph")
    #     print(f"Last Updated: {weather['last_updated']}")