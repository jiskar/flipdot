import requests, bs4
from flask import render_template
from app import app

@app.route('/index')
@app.route('/')
@app.route('/output')
@app.route('/day/<int:day>')
def output(day=0):
	# return word_of_the_day(day, alternate_site=True)
	return trending_on_twitter()


def word_of_the_day(day=0, alternate_site=False):
	wordlist = []
	if not alternate_site:
		response = requests.get('http://www.vandale.nl/woord-van-de-dag')
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		for node in soup.findAll("h2", { "class" : "woord-van-de-dag-title" }):
			wordlist.append(node.findAll(text=True))
	else:
		response = requests.get('http://www.taalbank.nl/index.php/category/woordvandedag/')
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		for node in soup.findAll("h1", { "class" : "uk-article-title" }):
			wordlist.append(node.findAll(text=True))
	try:
		return wordlist[day][0]
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