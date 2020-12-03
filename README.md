#### Introduction:
The purpose of this project is to create a smart alarm system in which the user can schedule alarms which will gather information about the current weather, news and COVID-19 information in their local area and then provide a text to speech alarm which will read out this information at a set time. The project also aims to provide a notification system which will notify the user when events occour during the day in text format. These notifications include notifying the user when the COVID-19 statistics are available for the current day in their current location and displaying the top news stories at set times of the day alongside a link to the full news articles.

#### Prerequisites:
An API key from openweathermap (openweathermap.org)
An API key from NewsAPI (newsapi.org)
A stable internet connection to allow for data to be gathered from the previously mentioned APIs
Python version 3.9 or above (developed using Python 3.9)

#### Installation:
Install pip and then run the command: pip install pyttsx3 (or pip3 install pyttsx3) in the terminal
Install pytest: pip install pytest (or pip3 install pytest)

#### Instructions:
Fill in the config file with the preference information listed bellow. Then run the main.py module and navigate to http://127.0.0.1:5000/ in the google chrome web browser.
Ensure that all sections are filled out in the config file with valid details otherwise the program will not work as expected.

Config file instructions:
preferences:
country: Fill in this section with the country you live in.
city: Fill in this section with the city you live in.
apptitle: Fill in this with the title to be displayed on the html template.
blacklist_sources: Fill in this with the list of sources you don't want to receive articles from, seperated by , e.g to blacklist The Sun and Daily Mirror: "The Sun, Daily Mirror".
number_of_articles: Fill this in with the number of articles you want to be displayed when news articles are requested.

API-keys:
weather: Fill in your API key from openweathermap.
news: Fill in your API key from News API.

filepaths:
logfile: Fill in the name of the log file which will keep logs of actions performed by the application and errors that occour.
image: Fill in the name of the image to be displayed on the application. This image should be stored in static/images.

#### Testing:
To run the test functions created to check if the functionality of the program is working correctly then navigate to the directory containing the files for the program and then run pytest.

#### Details:
Author: Cameron Stackhouse
Links to the source: https://github.com/cameronstackhouse/smart-alarm
Licence: GNU GPLv3  (www.gnu.org/licenses/gpl-3.0.en.html)




