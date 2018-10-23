import requests, bs4
from flask import render_template
from app import app
import json
import requests
import forex_python
import math

@app.route('/index')
@app.route('/')
@app.route('/output')
@app.route('/day/<int:day>')
def output(day=0):
    # return word_of_the_day(day, site='nytimes')
    return soarcast()
    # return bitcoinprice()


def jasper():
    r = requests.get('https://jaspervanloenen.com/bord')
    text = r.text.rstrip()
    print text
    return text


def bitcoinprice():
    from forex_python.bitcoin import BtcConverter
    b = BtcConverter() # force_decimal=True to get Decimal rates
    price = b.get_latest_price('EUR')
    price = math.floor(price)
    price = int(price)
    print
    return "BTC: " + str(price) + " EUR"


def word_of_the_day(day=0, site='taalbank'):
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
    #Import the necessary methods from tweepy library
    import tweepy, json, random
    from credentials import *

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
    wordlist = []
    try:
        response = json.loads(requests.get('http://one-word-news-server.cfapps.io/headlines/uk/all').text)
        word = response['World']['word']
        return word
    except:
        return ''


# ideas:
# gold to eur value
# use the sound as an alarm
# date
# word clock ('time for bed, time to wake up')


def soarcast():
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
        # for day, chance in sorted(days.iteritems()):
            # print "{}-> {}% chance on soaring!".format(day.strftime("%a"), chance)

        # show the first event:
        first_event = sorted(days)[0]
        # return "soaring {} {}% chc".format(first_event.strftime("%a").lower(), days[first_event])
        return "{} {}% chc!".format(first_event.strftime("%a").lower(), days[first_event])
    else:
        return ''