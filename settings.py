import os

APP_ID = 'gratitudereminder'

if (os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine') or
    os.getenv('SETTINGS_MODE') == 'prod'):
  PROD = True
  URL = 'gratitudereminder.org'
else:
  PROD = False
  URL = 'localhost:8080'

DEBUG = not PROD