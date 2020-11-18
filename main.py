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

def remove_alarm(alarm_item: str, alarms: list) -> None:
      for alarm in alarms:
            if alarm['title'] == alarm_item:
                  index = alarms.index(alarm)
                  alarms.pop(index)

def remove_notification(notification_item: str, notifications: str) -> None:
      for notification in notifications:
            if notification['title'] == notification_item:
                  index = notifications.index(notification)
                  notifications.pop(index)

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
          return None
      return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
          minutes_to_seconds(hhmm.split(':')[1])

def get_config() -> (str, str, str, str):
    """Gets all user entered data from the config file"""
    with open('config.json', 'r') as myfile:
        data = myfile.read()
    config_obj = json.loads(data)
    item =config_obj['config']
    keys = config_obj['API-keys']
    news_key = keys['news']
    weather_key = keys['weather']
    country = item['country']
    city = item['city']
    return news_key, weather_key, country, city
    

def k2c(kelvin: float) -> float:
    """Converts temperature in kelvin to celsius"""
    celsius = kelvin - 273.15
    celsius = round(celsius,2)
    return celsius

def covid_infection_rate(cases: int) -> str:
    """Returns the danger level of the area based on the number of cases"""
    if not isinstance(cases, int) or cases < 0:
        return "Error, cases in wrong datatype"
    elif cases > 250:
        return "High"
    elif cases > 150:
        return "Medium"
    elif cases > 50:
        return "Low"

@app.route('/')
def home() -> str:
    return render_template('main.html', title = 'Daily Update', notifications = set_notifications, alarms = set_alarms)
    
@app.route('/index')
def schedule_event() -> str:
    s.run(blocking = False)
    new_alarm = dict()
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
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        time = alarm_time[11:16]
        delay = hhmm_to_seconds(time) - hhmm_to_seconds(current_time)
        print(delay)
        if delay >= 0:
            s.enter(int(delay), 1, set_notification, (news, weather))
            new_alarm['title'] = alarm_title
            new_alarm['content'] = f'Alarm set for {time} on {alarm_time[0:10]}'
            set_alarms.append(new_alarm)
    return render_template('main.html', title = 'Daily Update', notifications = set_notifications, alarms = set_alarms)

@app.route('/tts_request')
def tts_request(announcement="Text to speech example announcement!") -> str:
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()
    return render_template('main.html', title = 'Daily Update', notifications = set_notifications, alarms = set_alarms)

@app.route('/set_notification')
def set_notification(news, weather) -> str:
    body = ''
    new_notif = dict()
    new_notif['title'] = 'Alarm activated'
    if weather:
          current_temp, current_pressure, current_humidity, weather = get_weather(weather_key, city)
          body += f'Current temperature in {city}: {k2c(current_temp)} degrees celcius.\n Weather description: {weather}.\n'
    if news:
          top_stories = get_news(news_key, country)
          for i in top_stories.keys():
                body += i + '\n'
    new_notif['content'] = body
    set_notifications.append(new_notif)
    return render_template('main.html', title = 'Daily Update', notifications = set_notifications, alarms = set_alarms)
    
    
news_key, weather_key, country, city = get_config()
current_covid = get_covid()

if __name__ == '__main__':
    app.run()





    


