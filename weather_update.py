import requests
import json

def get_weather(api_key, city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = json.loads(response.text)
    if x['cod'] != '404':
        y = x["main"]
        temperature = y["temp"]
        pressure = y["pressure"]
        humidity = y["humidity"]
        weather = x["weather"]
        current_weather = weather[0]["description"]
        
    return temperature, pressure, humidity, current_weather
