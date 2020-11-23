"""
Main Python file to run to run the alarm system
"""
import sched
import json
import time
import logging
from datetime import datetime
import pyttsx3
from flask import Flask, request, render_template
from news_filter import get_news
from weather_update import get_weather
from covid_update import get_covid


app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
set_alarms = list()
set_notifications = list()
dismissed_notifications = list()



def remove_alarm(alarm_item: str, alarms: list) -> None:
    """Removes a given alarm from the set_alarm list."""
    for alarm in alarms:
        if alarm['title'] == alarm_item:
            index = alarms.index(alarm)
            alarms.pop(index)


def remove_notification(notification_item: str, notifications: str) -> None:
    """Removes a given notificaiton from the set_notifications list."""
    for notification in notifications:
        if notification['title'] == notification_item:
            index = notifications.index(notification)
            old_notif = notifications.pop(index)
            dismissed_notifications.append(old_notif)


def days_to_hours(days: str) -> int:
    """Converts days to hours"""
    return int(days)*24


def minutes_to_seconds( minutes: str ) -> int:
    """Converts minutes to seconds"""
    return int(minutes)*60


def hours_to_minutes( hours: str ) -> int:
    """Converts hours to minutes"""
    return int(hours)*60


def hhmm_to_seconds( hhmm: str ) -> int:
    if len(hhmm.split(':')) != 2:
        print('Incorrect format. Argument must be formatted as HH:MM')
        logging.error('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])


def get_config() -> (str, str, str, str, str, str):
    """Gets all user entered data from the config file"""
    with open('config.json', 'r') as myfile:
        data = myfile.read()
    config_obj = json.loads(data)
    item = config_obj['config']
    keys = config_obj['API-keys']
    filepaths = config_obj['filepaths']
    news_key = keys['news']
    weather_key = keys['weather']
    country = item['country']
    city = item['city']
    app_title = item['apptitle']
    logfile_path = filepaths['logfile']
    return news_key, weather_key, country, city, app_title, logfile_path


def k2c(kelvin: float) -> float:
    """Converts temperature in kelvin to celsius"""
    try:
        celsius = kelvin - 273.15
        celsius = round(celsius,2)
    except TypeError:
        celcius = None
    return celsius


def covid_infection_rate(cases: int) -> str:
    """Returns the risk level of the area based on the number of cases"""
    if not isinstance(cases, int) or cases < 0:
        logging.error("Cases in an incorrect datatype")
        return "Error, cases in an incorrect datatype"
    elif cases > 250:
        return "Very High"
    elif cases > 150:
        return "High"
    elif cases > 50:
        return "Medium"
    elif cases >= 0:
        return "Low"


def activate_alarm(time: str, news: str, weather: str, config_city: str, date: str, title: str):
    """Function activate an alarm, reading out aloud the contents of the alarm."""
    body = ''
    count = 0
    cases, deaths, covid_date = get_covid(str(config_city), str(date))
    body += f'Registered COVID-19 cases in {config_city} today: {cases}. '
    alarm_title = f'{time}: {title}'
    if news:
        top_stories = get_news(news_key, country)
        if top_stories:
            for i in top_stories.keys():
                body += i + '. '
                count += 1
                if count == 3:
                    break
        else:
            body += 'No news stories to show. '
    if weather:
        current_temp, current_pressure, current_humidity, weather = get_weather(weather_key, city)
        if current_temp:
            temp_celcius = k2c(current_temp)
        else:
            temp_celcius = None
        body += f'Current temperature: {temp_celcius} degrees celcius.\n Weather description: {weather}. '
    tts_request(body)
    remove_alarm(title, set_alarms)

def set_notification(title, body) -> dict:
    new_notif = dict()
    new_notif['title'] = title
    new_notif['content'] = body
    return new_notif

def set_alarm(title, body):
    new_alarm = dict()
    new_alarm['title'] = title
    new_alarm['content'] = body
    set_alarms.append(new_alarm)


@app.route('/')
@app.route('/index')
def schedule_event() -> str:
    """Function to check for user input on various areas of the HTML page.
      The function gets all data the user has entered into the HTML page.
      Checks to see if the user has entered an alarm, if so then an alarm is scheduled.
      Also checks to see if the user has requested for a notification or alarm to be
      deleted and removed and removes the item."""
    s.run(blocking = False)
    now = datetime.now()
    current_date = datetime.today().strftime('%Y-%m-%d')
    cases, deaths, date = get_covid(city, current_date)
    alarm_item = request.args.get("alarm_item")
    alarm_time = request.args.get("alarm")
    notification_item = request.args.get("notif")
    if alarm_item:
        remove_alarm(alarm_item, set_alarms)
    elif notification_item:
        remove_notification(notification_item, set_notifications)
    elif alarm_time:
        alarm_title = request.args.get("two")
        news = request.args.get("news")
        weather = request.args.get("weather")
        current_time = now.strftime("%H:%M")
        time = alarm_time[11:16]
        set_date = alarm_time[:10].split('-')
        current_date_convert = current_date.split('-')
        set_year, set_month, set_day = int(set_date[0]), int(set_date[1]), int(set_date[2])
        now_year, now_month, now_day = int(current_date_convert[0]), int(current_date_convert[1]), int(current_date_convert[2])
        set_date = datetime(set_year, set_month, set_day).date()
        current_date_convert = datetime(now_year, now_month, now_day).date()
        difference = set_date - current_date_convert
        days_difference = difference.days
        delay = (hhmm_to_seconds(time) - hhmm_to_seconds(current_time)) + days_difference * 86400
        if delay >= 0:
            alarm_title = alarm_title + ' set for: ' + str(time) + ' ' + str(set_date)
            s.enter(int(delay), 1, activate_alarm, (time, news, weather, city, set_date, alarm_title))
            set_alarm(alarm_title, f'News Stories: {news}. Weather Report: {weather}.')
        else:
            logging.error('Invalid date entered, date and time is behind the current date and time')
    if cases is not None:
        new_notif = set_notification(str(current_date) + ' COVID-19 Update', f'COVID-19 Statistics for {city} for today are now available')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
    else:
        new_notif = set_notification(str(current_date) + ' COVID-19 Update', f'COVID-19 Statistics for {city} for today are not yet available')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
    current_time = now.strftime("%H:%M")
    count = 0
    if current_time in ['8:00', '18:00', '22:00']:
        top_stories = get_news(news_key, country)
        body = ''
        if top_stories:
            for i in top_stories.keys():
                body += i + ' '
                body += top_stories[i] + '. '
                count += 1
                if count == 3:
                    break
        new_notif = set_notification(str(current_date) + ' ' + str(current_time) + ' News update', body)
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
    infection_rate = covid_infection_rate(cases)
    if infection_rate in ['PLACEHOLDER']:
        new_notif = set_notification('Placeholder Title', 'Placeholder Content')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
    return render_template('main.html', title = web_title, notifications = set_notifications, alarms = set_alarms)


@app.route('/tts_request')
def tts_request(announcement="Text to speech example announcement!") -> str:
    """Function to perform text to speech on a given text input."""
    pyttsx3.speak(announcement)
    return render_template('main.html', title = web_title, notifications = set_notifications, alarms = set_alarms)


if __name__ == '__main__':
    news_key, weather_key, country, city, web_title, logfile = get_config()
    logging.basicConfig(filename=logfile, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
    app.run()
