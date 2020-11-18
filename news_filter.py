import requests
import json

def get_news(api_key, country) -> dict:
    """Returns the top news stories for the current time given a specific country
    stated in the config file"""
    stories = dict()
    try:
        base_url = "https://newsapi.org/v2/top-headlines?"
        complete_url = base_url + "country=" + country + "&apiKey=" + api_key
        response = requests.get(complete_url)
        x = json.loads(response.text)
        for article in x['articles']:
            title = article['title']
            link = article['url']
            stories[title] = link
    except:
        print(f'api key of {api_key} is invalid')
        
    return stories
