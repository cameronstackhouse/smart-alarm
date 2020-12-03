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
engine = pyttsx3.init()


def remove_alarm(alarm_item: str, alarms: list) -> None:
    """Removes a given alarm from the set_alarm list and removes
    the dismissed alarm from the scheduler if it is in the
    scheduler queue"""
    found = False
    for alarm in alarms:
        if alarm['title'] == alarm_item:
            index = alarms.index(alarm)
            alarm_event = alarm['event']
            alarms.pop(index)
            if alarm_event in s.queue:
                s.cancel(alarm_event)
            logging.info(f'Alarm {alarm_item} has been removed')
            found = True
            break
    if not found:
        logging.error(f'Alarm {alarm_item} not found')


def remove_notification(notification_item: str, notifications: list) -> None:
    """Removes a given notificaiton from the set_notifications list"""
    found = False
    for notification in notifications:
        if notification['title'] == notification_item:
            index = notifications.index(notification)
            old_notif = notifications.pop(index)
            dismissed_notifications.append(old_notif)
            logging.info(f'Notification {old_notif} has been removed')
            found = True
            break
    if not found:
        logging.error(f'Notification {notification_item} not found')

def days_to_hours(days: str) -> int:
    """Converts days to hours"""
    return int(days)*24


def minutes_to_seconds(minutes: str) -> int:
    """Converts minutes to seconds"""
    return int(minutes)*60


def hours_to_minutes(hours: str) -> int:
    """Converts hours to minutes"""
    return int(hours)*60


def hhmm_to_seconds(hhmm: str) -> int:
    """Converts HH:MM to seconds"""
    if len(hhmm.split(':')) != 2:
        logging.error('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])


def get_config(filename: str) -> (str, str, str, str, str, str, list, int, str):
    """Gets all user entered data from the config file"""
    with open(filename, 'r') as myfile:
        data = myfile.read()
    config_obj = json.loads(data)
    preferences = config_obj['preferences']
    keys = config_obj['API-keys']
    filepaths = config_obj['filepaths']
    news_key = keys['news']
    weather_key = keys['weather']
    country = preferences['country']
    city = preferences['city']
    app_title = preferences['apptitle']
    blacklist_sources = preferences['blacklist_sources'].split(', ')
    number_of_articles = preferences['number_of_articles']
    logfile_path = filepaths['logfile']
    image = filepaths['image']
    return news_key, weather_key, country, city, app_title, logfile_path, blacklist_sources,\
    number_of_articles, image


def k2c(kelvin: float) -> float:
    """Converts temperature in kelvin to celsius"""
    try:
        celsius = kelvin - 273.15
        celsius = round(celsius,2)
    except TypeError:
        celsius = None
    return celsius


def covid_infection_rate(cases: int) -> str:
    """Returns the risk level of the area based on the number of cases"""
    if not isinstance(cases, int) or cases < 0:
        logging.error("Cases in an incorrect datatype or not available yet")
        risk_level = None
    elif cases > 250:
        risk_level = "Very High"
    elif cases > 150:
        risk_level = "High"
    elif cases > 50:
        risk_level = "Medium"
    elif cases >= 0:
        risk_level = "Low"
    return risk_level


def add_stories(key: str, area: str, articles: int, blist: list, links = False) -> str:
    """Function return the top stories of the day given different perameters from the config file.
    The function only returns the number of top stories the user has specified they want to see,
    this is specified in the articles variable."""
    body = ''
    count = 0
    top_stories = get_news(key, area)
    if top_stories:
        try:
            for title in top_stories.keys():
                split_title = title.split('-')
                source = str(split_title[len(split_title) - 1])
                if source.strip() in blist or int(articles) <= 0:
                    pass
                else:
                    body += title + '. '
                    if links:
                        body += top_stories[title] + '. '
                    count += 1
                if count == int(articles) or count >= len(top_stories.keys()):
                    break
        except TypeError:
            body += 'No news stories to show. '
            logging.error('Invalid news config details, ensure all sections are filled in and are in the correct datatypes')
        except ValueError:
            body += 'No news stories to show. '
            logging.error('Invalid news config details, ensure all sections are filled in and are in the correct datatypes')
    else:
        body += 'No news stories to show. '
        logging.error('No news stories to show')
    return body


def activate_alarm(time: str, news: str, weather: str, config_city: str, date: str, title: str) -> None:
    """Function activate an alarm, reading out aloud the contents of the alarm that has been set"""
    body = ''
    count = 0
    cases, deaths, covid_date = get_covid(str(config_city), str(date))
    body += f'Registered COVID-19 cases in {config_city} today: {cases}. '
    alarm_title = f'{time}: {title}'
    if news:
        stories = add_stories(news_key, country, num_articles, blacklist)
        body += stories
    if weather:
        current_temp, current_pressure, current_humidity, weather = get_weather(weather_key, city)
        temp_celsius = k2c(current_temp)
        body += f'Current temperature: {temp_celsius} degrees celcius.\n Weather description: {weather}. '
    tts_request(body)
    remove_alarm(title, set_alarms)
    logging.info(f'Alarm: {title} has been activated')

def set_notification(title: str, body: str) -> dict:
    """Creates a new notification given a title and body"""
    new_notif = dict()
    new_notif['title'] = title
    new_notif['content'] = body
    return new_notif

def set_alarm(title: str, body: str, set_event: str) -> dict:
    """Creates a new alarm given a title, body and event from the scheduler"""
    new_alarm = dict()
    new_alarm['title'] = title
    new_alarm['content'] = body
    new_alarm['event'] = set_event
    return new_alarm


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
        try:
            set_year, set_month, set_day = int(set_date[0]), int(set_date[1]), int(set_date[2])
            now_year, now_month, now_day = int(current_date_convert[0]), int(current_date_convert[1]), int(current_date_convert[2])
            set_date = datetime(set_year, set_month, set_day).date()
            current_date_convert = datetime(now_year, now_month, now_day).date()
            difference = set_date - current_date_convert
            days_difference = difference.days
            delay = (hhmm_to_seconds(time) - hhmm_to_seconds(current_time)) + \
                    days_difference * 86400
        except ValueError:
            delay = -1
            logging.error('Date entered is out of range')
        if delay >= 0:
            alarm_title = alarm_title + ' set for: ' + str(time) + ' ' + str(set_date)
            event = s.enter(int(delay), 1, activate_alarm, (time, news, weather, city, set_date, alarm_title))
            alarm_body = f'Alarm speech annoncement containing number of covid cases for the day in {city}'
            if news:
                alarm_body += ' and the top news stories'
            if weather:
                alarm_body += ' and the current weather'
            new_alarm = set_alarm(alarm_title, alarm_body, event)
            set_alarms.append(new_alarm)
            logging.info(f'Alarm named {alarm_title}')
        else:
            logging.error(f'Invalid date and time entered: {set_date} {time}')
    if cases is not None:
        new_notif = set_notification(str(current_date) + ' COVID-19 Update', f'COVID-19 Statistics for {city} for today are now available')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
            logging.info(f'Notification: {new_notif} set')
    else:
        new_notif = set_notification(str(current_date) + ' COVID-19 Update', f'COVID-19 Statistics for {city} for today are not yet available')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
            logging.info(f'Notification: {new_notif} set')
    current_time = now.strftime("%H:%M")
    count = 0
    if current_time in ['8:00', '12:00', '18:00', '22:00', '00:00']:
        body = add_stories(news_key, country, num_articles, blacklist, True)
        new_notif = set_notification(str(current_date) + ' ' + str(current_time) + ' News update', body)
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
            logging.info(f'Notification: {new_notif} set')
    infection_rate = covid_infection_rate(cases)
    if infection_rate in ['Low', 'Medium', 'High', 'Very High']:
        new_notif = set_notification(f'COVID-19 Infection rate {str(current_date)}', f'The current covid infection rate in {city} is {infection_rate}')
        if new_notif not in dismissed_notifications and new_notif not in set_notifications:
            set_notifications.append(new_notif)
            logging.info(f'Notification: {new_notif} set')
    return render_template('main.html', title = web_title, notifications = set_notifications, alarms = set_alarms, image = set_image)


@app.route('/tts_request')
def tts_request(announcement: str ="Text to speech example announcement!") -> str:
    """Function to perform text to speech on a given text input"""
    try:
        engine.endLoop()
    except:
        logging.error('PyTTSx3 Endloop error')
    engine.say(announcement)
    engine.runAndWait()
    return render_template('main.html', title = web_title, notifications = set_notifications, alarms = set_alarms, image = set_image)


if __name__ == '__main__':
    try:
        news_key, weather_key, country, city, web_title, logfile, blacklist, num_articles, set_image = get_config('config.json')
        failed = False
    except:
        failed = True
        news_key, weather_key, country, city, web_title, logfile, blacklist, num_articles, set_image = '', '', '', '', '', 'app.log', [], 0, ''
    logging.basicConfig(filename=logfile, level=logging.INFO, filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger('werkzeug').disabled = True
    if failed:
        logging.error('One or more config fields are in an invalid data type')
    app.run()
