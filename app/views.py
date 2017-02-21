import requests, bs4
from flask import render_template
from app import app

@app.route('/index')
@app.route('/')
@app.route('/output')
@app.route('/day/<int:day>')
def output(day=0):
	return word_of_the_day(day, site='nytimes')


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
		return 'exception'
