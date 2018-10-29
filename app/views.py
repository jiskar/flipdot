# -*- coding: utf-8 -*-

import requests, bs4
from flask import render_template
from app import app
import json
import requests
import forex_python
import datetime
import os

# Max characters on flipdotboard:
# abcdefghi > large font
# abcdefghijkl > medium font
# abcdefghijklmno > small font

@app.route('/index')
@app.route('/')
@app.route('/output')
@app.route('/day/<int:day>')
def output(day=0):
    # This is the view that the photon requests. The string returned here will be shown on the flipdotboard.
    soaralert = soarcast()
    if soaralert:
        return soaralert
    else:
        return weather()


def weather():
    import pyowm
    api_key = os.environ.get('OWM_API_KEY')  # pull from heroku's config vars
    owm = pyowm.OWM(api_key)  # You MUST provide a valid API key

    # Search for current weather in Rotterdam
    observation = owm.weather_at_place('Rotterdam,NL')
    w = observation.get_weather()
    try:
        # print(w)                      # <Weather - reference time=2013-12-18 09:20,
        # print w.get_wind()                  # {'speed': 4.6, 'deg': 330}
        # print w.get_humidity(), '%'              # 87
        # print w.get_visibility_distance()
        # status = w.get_status()
        rain = w.get_rain()
        snow = w.get_snow()
        temperature = w.get_temperature('celsius')['temp']  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
        temperature = int(round(float(temperature)))

        if rain != {}:
            report = "{}*C R".format(temperature)
        elif snow != {}:
            report = "{}*C S".format(temperature)
        else:
            report = "{}*C".format(temperature)

        return date() + " " + report
    except Exception as e:
        print e
        return date()

def date():
    return datetime.datetime.now().strftime("%d %b")

def friendly_server():
    # pulls a string directly from a URL:
    r = requests.get(os.environ.get('FRIENDLY_SERVER_URL'))
    text = r.text.rstrip()
    print text
    return text

def bitcoinprice():
    # shows the current btc price
    from forex_python.bitcoin import BtcConverter
    b = BtcConverter() # force_decimal=True to get Decimal rates
    price = b.get_latest_price('EUR')
    price = math.floor(price)
    price = int(price)
    print
    return "BTC: " + str(price) + " EUR"


def word_of_the_day(day=0, site='taalbank'):
    # shows the word of the day
    wordlist = []
    if site == 'taalbank':
        response = requests.get('http://www.taalbank.nl/index.php/category/woordvandedag/')
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for node in soup.findAll("h2", { "class" : "entry-title" }):
            text = ''.join(node.findAll(text=True))
            text.encode('ascii', 'ignore')
            wordlist.append(text)
        wordlist.pop(0)
    elif site == 'nytimes':
        response = requests.get('https://www.nytimes.com/column/learning-word-of-the-day')
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for node in soup.findAll("h2", { "class" : "headline" }):
            text = ''.join(node.findAll(text=True))
            # print text
            text = text.split('Word + Quiz: ')[1].strip()
            text.encode('ascii', 'ignore')
            wordlist.append(text)
    print wordlist
    try:
        return wordlist[day]
    except:
        return ''


def trending_on_twitter():
    # shows the top trending word on twitter
    import tweepy, json, random
    from credentials import auth

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    trends1 = api.trends_place(23424909)
    hashtags = [x['name'] for x in trends1[0]['trends'] if x['name'].find('#') ==0]
    print hashtags
    output = ''
    # for hashtag in hashtags:
        # output += hashtag + '<br>'
    return random.choice(hashtags)

def onewordnews():
    # pulls the one word from onewordnews.com
    wordlist = []
    try:
        response = json.loads(requests.get('http://one-word-news-server.cfapps.io/headlines/uk/all').text)
        word = response['World']['word']
        return word
    except:
        return ''


def soarcast():
    # checks for nice paraglider-soaring winds.
    # if the weather is good, returns a day and chance on soaring like "wed -> 90% chance on soaring"
    import urllib2
    from icalendar import Calendar

    url = "http://soarcast.nl/sc/overview.php?timeOffset=0&formSubmitted=true&soaren=on&bigwing=on&spot_1=on&changeValues=Wijzig+selectie&ical=true"
    contents = urllib2.urlopen(url).read()

    days = {}

    # create a list of days and their chance on soaring:
    gcal = Calendar.from_ical(contents)
    for component in gcal.walk():
        if component.name == "VEVENT":
            date = component.get('dtstart').dt.date()
            summary = component.get('summary').title()
            chance = int(summary[-3:-1])
            if not date in days.keys():
                days[date] = chance
            elif days[date] < chance:
                days[date] = chance
    if days:
        # show the first event:
        first_event = sorted(days)[0]
        return "{} {}% soar!".format(first_event.strftime("%a").lower(), days[first_event])
    else:
        return ''