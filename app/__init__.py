from flask import Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.debug = True

if os.environ.get('IS_HEROKU', None):  # if we are running on heroku (you need to set the config variable 'IS_HEROKU' manually)
    pass  # heroku sets environmental variables
else:
    load_dotenv()
    print '[Not running on heroku, loading local .env]'


from app import views