"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'some key here'

app.config.from_pyfile('settings.py')

import car_rent.views
