"""
Module containing the function to get information about a given areas weather
"""
import json
import logging
import requests

def get_weather(api_key, city_name):
    """
    Function to get the current weather and temperature of a
    given city using the openweathermap API
    @param api_key: this is the API key for openweathermap
    @param city_name: this is the city to get weather details for
    @return: returns the temperature, pressure, humidity and
    current weather description of the given place
    @raise KeyError: raises an error if no data is retrieved
    (this could be due to invalid API key or invalid city name)
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    try:
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        weather_json = json.loads(response.text)
        if weather_json['cod'] != '404':
            main_data = weather_json["main"]
            temperature = main_data["temp"]
            pressure = main_data["pressure"]
            humidity = main_data["humidity"]
            weather = weather_json["weather"]
            current_weather = weather[0]["description"]
        else:
            temperature, pressure, humidity, current_weather = None, None, None, None
            logging.error('invalid API key for openweathermap')
    except KeyError:
        temperature, pressure, humidity, current_weather = None, None, None, None
        logging.error('no weather data for given area or invalid API key for openweathermap') 
    return temperature, pressure, humidity, current_weather

