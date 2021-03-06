import os

APP_NAME = 'Idea Reminder'

APP_ID = 'idea-reminder'
TEMPLATE_ID = '1ReEXwavfCe1XSndkTv645iTYWv9jBrhz7iucS4TARv0'
EMAIL_SENDER = 'Idea Reminder <postman@idea-reminder.appspotmail.com>'
GITHUB_URL = 'https://github.com/maxh/idea-reminder/issues'

if (os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine') or
    os.getenv('SETTINGS_MODE') == 'prod'):
  PROD = True
  URL = 'ideareminder.org'
else:
  PROD = False
  URL = 'localhost:8080'

DEBUG = not PROD