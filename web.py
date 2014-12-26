""" web.py:
    Handles incoming requests from web users.
"""

# Python library imports.
from datetime import datetime
import jinja2
import json
import logging
import os
import webapp2

# App Engine imports.
from google.appengine.ext import ndb
from google.appengine.api import users

# File imports.
from secrets import keys
import drive
import link
import mail
import models
import settings


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__) + '/templates/web/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        not_registered_urls = {
            'sign_up_link': users.create_login_url('/register'),
            'sign_in_link': users.create_login_url('/'),
        }
        if self.request.get('sup') == 'error':
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render())
            return
        # User is not logged in.
        user = users.get_current_user()
        if not user:
            template = JINJA_ENVIRONMENT.get_template('not_registered.html')
            self.response.write(template.render(not_registered_urls))
            return
        # User _just_ registered and may not be in the DB yet.
        if (self.request.get('sup') == 'just_registered'):
            template = JINJA_ENVIRONMENT.get_template('just_registered.html')
            self.response.write(template.render(user_email=user.email()))
            return
        users_db = models.User.query(models.User.email == user.email()).fetch(1)
        # User is logged in but not signed up.
        if len(users_db) == 0:
            template = JINJA_ENVIRONMENT.get_template('not_registered.html')
            self.response.write(template.render(not_registered_urls))
            return
        # User is logged in and registered.
        user_db = users_db[0]
        status = 'registered'
        template = JINJA_ENVIRONMENT.get_template('registered.html')
        if self.request.get('sup') == 'already_registered':
            status = 'already_registered'
        self.response.write(template.render(
            user_status=status,
            user_email=user_db.email,
            sign_out_link=users.create_logout_url('/'),
            responses_link=link.spreadsheet(user_db.file_id),
            unsubscribe_link=link.unsubscribe(user_db.email)))



class Register(webapp2.RequestHandler):

    def get(self):
        try:
            user = users.get_current_user()
            email = user.email()
            if len(models.User.query(models.User.email == email).fetch(1)) == 1:
                self.redirect("/?sup=already_registered")
                return
            file_id = drive.create_responses_spreadsheet(email)
            user = models.User(email=email, file_id=file_id)
            user.put()
            mail.send_email_from_template(email, file_id, 'welcome')
        except Exception as e:
            logging.exception('Exception while registering:')
            logging.exception(email)
            logging.exception(e)
            self.redirect('/?sup=error')
        self.redirect('/?sup=just_registered')


class Unsubscribe(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            email = user.email()
        else:
            email = self.request.get('email')
        try:
            if not email:
                raise Exception('No email specified.')
            users_db = models.User.query(models.User.email == email).fetch(1)
            if len(users_db) == 0:
                raise Exception('Email address not in our database.')
            user = users_db[0]
            file_id = user.file_id
            # TODO: Mark user as unsubscribed instead of deleting entry.
            user.key.delete()
            mail.send_email_from_template(email, file_id, 'unsubscribe')
        except Exception as e:
            logging.exception('Exception while unsubscribing:')
            logging.exception(email)
            logging.exception(e)
            self.redirect('/?sup=error')
        self.response.write('Successfully unsubscribed.')


routes = [
    ('/', MainPage),
    ('/register', Register),
    ('/unsubscribe', Unsubscribe),
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)
