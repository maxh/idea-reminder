""" drive.py:
    Helper functions for interfacing with the Drive & Spreadsheet APIs.
"""

import logging
from datetime import datetime
import re
import xml.etree.ElementTree as ET

#import lib # All third-party libraries are in this module.
import lib
import gdata.spreadsheets.client
import gdata.spreadsheet.service
import gdata.client
import gdata.service
import httplib2
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials

import settings
from secrets import keys


def create_authorized_http(scope):
    credentials = AppAssertionCredentials(scope)
    http = httplib2.Http()
    return credentials.authorize(http)


def create_drive_service(http=None):
    # https://developers.google.com/drive/web/service-accounts
    if http is None:
        http = create_authorized_http(
            scope='https://www.googleapis.com/auth/drive')
    # When running in debug mode on the dev_appserver, service accounts require
    # a few flags to be set. See: http://stackoverflow.com/a/22723127/1691482
    # These flags don't play nice with the api_key.
    if (settings.DEBUG):
      return build('drive', 'v2', http=http)
    return build('drive', 'v2', http=http, developerKey=keys.api_key)


def create_spreadsheet_service():
    try:
        logging.info('Creating spreadsheet service now.')
        http = create_authorized_http('https://spreadsheets.google.com/feeds')
        create_drive_service(http) # Not sure why this is necessary. Inspired by
                                   # http://stackoverflow.com/a/21468060/1691482
        service = gdata.spreadsheet.service.SpreadsheetsService()
        service.additional_headers = {'Authorization': 'Bearer %s' %
                                      http.request.credentials.access_token}
        return service
    except Exception as e:
        logging.exception(e)
        raise


def give_user_ownership(service, file_id, user_email):
    new_permission = {
      'value': user_email,
      'type': 'user',
      'role': 'owner'
    }
    logging.info('Giving ownership of spreadsheet to:')
    logging.info(str(user_email))
    try:
        return service.permissions().insert(fileId=file_id, body=new_permission,
            sendNotificationEmails=False).execute()
    except Exception as e:
        logging.exception(e)
        raise


def create_responses_spreadsheet(user_email):
    try:
        start = datetime.now()
        service = create_drive_service()
        logging.info(service)
        body = {'title': 'Idea Reminder Responses'}
        copy = service.files().copy(
            fileId=settings.TEMPLATE_ID,
            body=body).execute()
        copy_id = copy['id']
        give_user_ownership(service, copy['id'], user_email)
        logging.info('Time spent in create_responses_spreadsheet')
        logging.info(datetime.now() - start)
        # This takes too long.
        # TODO: https://developers.google.com/appengine/docs/python/taskqueue/
        return copy_id
    except Exception as e:
        logging.exception(e)
        raise


def add_gratitude_response(file_id, response, date):
    """Appends the response to the spreadsheet indicated by file_id."""
    try:
        logging.info('Adding response now.')
        service = create_spreadsheet_service()
        worksheets = service.GetWorksheetsFeed(key=file_id)
        worksheet = worksheets.entry[0]
        id_xml = ET.fromstring(str(worksheet.id))
        # Extract the worksheet id from the XML.
        ws_id = re.sub(r'^.*full/(.*)$', r'\1', id_xml.text)
        row_data = {'date': date,
                    'response': response}
        service.InsertRow(row_data=row_data, key=file_id, wksht_id=ws_id)
    except Exception as e:
        logging.exception(e)
        raise
