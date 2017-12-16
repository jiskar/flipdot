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
	# return jasper()
	return bitcoinprice()


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
