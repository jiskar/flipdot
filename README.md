# flipdot

This app can push texts like the current date, weather, twitter trends, etc to a krueger flipdot/dotmatrix sign. These signs were used in buses aroud europe to show the line number and destination. The sign that i'm using can display two lines of 15 characters.

The app pulls info from various internet sources and parses it to a single string that will fit the board. A flask app serves this string to the web.
A particle photon requests this string by polling the webserver. It calculates the necessary control characters needed for the IBIS protocol and then sends the text via a serial interface to the dotmatrix sign.

The photon and dotmatrix are plugged in via a timer socket so that they are active twice a day for two minutes only. That's enough to boot, connect to wifi and make a poll to the server.

# Installation:
I run the main app on [heroku](https://www.heroku.com/). You can run it on any machine that runs python though.
To publish new code, run:

'git push heroku'

you need to set two config vars in heroku:

* IS_HEROKU = True
* OWM_API_KEY = 'your_free_openweathermap_api_key'

flipdot.ino runs on a Particle Photon which is programmed via the [web-ide](http://build.particle.io/)

# Hardware:
* 2001 Krueger 16x80 Dotmatrix with an MX3 control board
* [Particle photon](https://store.particle.io/)
* 24Vdc adapter
* voltage divider to create 19V from 24V
* Photon pin D6 is connected to a transistor switching the data line between 19V and ground