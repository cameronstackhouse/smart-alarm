import json
import requests
from weather_update import get_weather

def test_invalid_name():
    a, b, c, d = get_weather('194d48fe0d7ecdc5d7fd5c4fbdb28038', 'aaaa')
    assert (a, b, c, d) == (None, None, None, None)

def test_invalid_key():
    a, b, c, d = get_weather('aa', 'Exeter')
    assert (a, b, c, d) == (None, None, None, None)

def test_valid():
    a, b, c, d = get_weather('194d48fe0d7ecdc5d7fd5c4fbdb28038', 'Exeter')
    assert (a, b, c, d) != (None, None, None, None)

def test_none():
    a, b, c, d = get_weather('', '')
    assert (a, b, c, d) == (None, None, None, None)

def test_connection():
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=194d48fe0d7ecdc5d7fd5c4fbdb28038&q=London" 
    response = requests.get(complete_url)
    weather_json = json.loads(response.text)
    assert weather_json['cod'] != '404'
    
