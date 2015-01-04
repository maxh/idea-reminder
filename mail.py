""" mail.py:
    Sends reminder emails and handles their responses and defines a few helper
    functions for sending email.
"""

from datetime import datetime
import jinja2
import logging
import os
import re
import webapp2

# App Engine imports.
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

# File imports.
import drive
import link
import models
import settings


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__) + '/templates/emails/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.globals = {
    'app_name': settings.APP_NAME,
    'github_url': settings.GITHUB_URL
}


class SendReminderEmails(webapp2.RequestHandler):

    def get(self):
        # Load the template in advance to avoid getting the template once for
        # each user.
        template = JINJA_ENVIRONMENT.get_template('reminder.html')
        users = models.User.query(models.User.unsubscribed == False).fetch()
        for user in users:
            send_email_from_template(user.email, user.file_id, template)


class ReminderReplyHandler(InboundMailHandler):

    def receive(self, mail_message):
        logging.info('Received a message from: ' + mail_message.sender)
        # Sender is formatted like "A B <ab@x.com>"; extract the email.
        sender_email = re.sub(r'.*<(.*@.*\..*)>.*', r'\1', mail_message.sender)
        # There might be multiple message bodies, but we'll only read the first.
        plaintext_body = mail_message.bodies('text/plain').next()[1].decode()
        stripping_regex = re.compile('(\n+On .*wrote.*:.*)', re.DOTALL)
        stripped_body = stripping_regex.sub(r'', plaintext_body)
        stripped_body = stripped_body.rstrip()
        users = models.User.query(models.User.email == sender_email).fetch(1)
        if len(users) == 0:
            raise Exception('Email address not in our database.')
        user = users[0]
        user.number_of_replies += 1
        user.put()
        logging.info('About to add a response for the user:' + str(user))
        drive.add_gratitude_response(
            file_id=user.file_id,
            response=stripped_body,
            date=datetime.today().strftime('%Y-%m-%d'))


routes = [
    ('/mail/send-reminders', SendReminderEmails),
    ('/_ah/mail/postman@.*', ReminderReplyHandler)
]

app = webapp2.WSGIApplication(routes, debug=settings.DEBUG)


##############################
### Mail helper functions. ###
##############################


def send_email_from_template(user_email, file_id, template):
    # template can be a string or an actual Jinja template.
    if isinstance(template, basestring):
        template = JINJA_ENVIRONMENT.get_template(template + '.html')
    html_body = template.render(
        format='html',
        responses_link=link.spreadsheet(file_id),
        unsubscribe_link=link.unsubscribe(user_email))
    body = template.render(
        responses_link=link.spreadsheet(file_id),
        unsubscribe_link=link.unsubscribe(user_email))
    send_email(user_email, template.module.subject, body, html_body)


def send_email(address, subject, body, html_body):
    message = mail.EmailMessage()
    message.to = address
    message.sender = settings.EMAIL_SENDER
    message.reply_to = settings.EMAIL_SENDER
    message.subject = subject
    message.body = body
    message.html = html_body
    message.send()
