import requests, bs4
from flask import render_template
from app import app

@app.route('/index')
@app.route('/')
@app.route('/output')
@app.route('/day/<int:day>')
def output(day=0):
	return word_of_the_day(day, alternate_site=True)


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
