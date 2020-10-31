from datetime import date
import time
import requests
import json
import pyttsx3
import sched
from plyer import notification
from uk_covid19 import Cov19API


def text_notification(header, body):
    notification.notify( 
            title = header, 
            message= body,
            )


def top_stories(key):
    stories_data = requests.get(f'http://newsapi.org/v2/top-headlines?country=gb&apiKey={key}')
    json_stories = json.loads(stories_data.text)
    return json_stories


def speech_notification(text):=
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def gen_body(cases, deaths, location, date):
    """Function to create the body of a text notification using COVID data gathered from COVID UK API"""
    return f'COVID-19 statistics for {location}, {date}:\nNew cases: {cases}\nNew deaths: {deaths}'
    


today = str(date.today())


england = [
    'areaType=nation',
    'areaName=England',
    'date='+today
    ]


cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate"
}

cases = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate"
}

deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate"
}

covid_data = Cov19API(filters=england, structure=cases_and_deaths)
j = covid_data.get_json()
s = top_stories('c1cbe821f0d24fb49be55f5c86172737')
list_of_days = j["data"]
if not list_of_days:
    text_notification("COVID-19 update", "Cases and deaths for your area today have not yet been released.")
else:
    day_dict = list_of_days[0]
    day_cases = day_dict["newCasesByPublishDate"]
    day_deaths = day_dict["newDeathsByDeathDate"]
    day_date = day_dict["date"]
    text_notification("COVID-19 daily update", (gen_body(day_cases, day_deaths, "England", day_date)))

    

