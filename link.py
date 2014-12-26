""" link.py: 
    Helper functions for generating links.
"""


import settings


def spreadsheet(file_id):
    return 'https://docs.google.com/spreadsheets/d/' + file_id


def unsubscribe(user_email):
    return 'http://www.' + settings.URL + '/unsubscribe?email=' + user_email