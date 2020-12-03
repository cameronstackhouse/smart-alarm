"""Module to get COVID-19 case data using the uk_covid19 API"""
import logging
from uk_covid19 import Cov19API
def get_covid(city: str, current_date: str) -> (int, int, str):
    """Function to get the number of covid-19 cases in a given area on
    a given date"""
    cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate"
    }
    try:
        current_location = ['areaName='+city]
        covid_api = Cov19API(filters = current_location, structure= cases_and_deaths)
        covid_data = covid_api.get_json()
        data = covid_data['data']
        if data:
            for day in data:
                if day['date'] == current_date:
                    cases = day['newCasesByPublishDate']
                    deaths = day['newDeathsByDeathDate']
                    date = day['date']
                    break
                else:
                    cases, deaths, date = None, None, None
        else:
            cases, deaths, date = None, None, None
    except:
        cases, deaths, date = None, None, None
        logging.error('Invalid area name entered')
    return cases, deaths, date











    
    
