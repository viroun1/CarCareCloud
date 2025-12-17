import requests

API_KEY = "a7bec1f3c457c620e481bd2d0816d5a8"

def get_weather(city):
    """
    Fetches current weather data from WeatherAPI.com.
    Returns temperature and condition as a dictionary.
    """

    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        return {
            "temp": data["current"]["temp_f"],
            "condition": data["current"]["condition"]["text"]
        }

    except:
        # If API fails, return default data so your app still works
        return {
            "temp": "N/A",
            "condition": "Unavailable"
        }
