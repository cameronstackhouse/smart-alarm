import json
import logging
import requests

def get_news(api_key: str, country: str) -> dict:
    """Returns the top news stories for the current time given a specific country
    stated in the config file"""
    stories = dict()
    try:
        base_url = "https://newsapi.org/v2/top-headlines?"
        complete_url = base_url + "country=" + country + "&apiKey=" + api_key
        response = requests.get(complete_url)
        news_data = json.loads(response.text)
        for article in news_data['articles']:
            title = article['title']
            link = article['url']
            stories[title] = link
    except KeyError:
        logging.error('No data for given area or invalid API key for newsAPI')
        stories = {}
    return stories
