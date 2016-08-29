## Google API
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# Google Sheets Constants
SHEET_ID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
DISCOVERY_URL = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
SHEET_NUMBER = 1
STARTING_CELL = 'A2'

APPLICATION_NAME = 'Google Sheets API Python Quickstart'
COLUMNS = {'title': 0, 
           'author': 1,
           'publisher': 2,
           'edition': 3,
           'dateCreated': 4,
           'genre': 5,
           'ddc': 6,
           'subject': 7}
SORT_BY = ['ddc','author','title']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http,
                               discoveryServiceUrl=DISCOVERY_URL)
    return service

def build_body(**kwargs):
    rangeName = 'Sheet%d!%s' % (SHEET_NUMBER,STARTING_CELL)
    majorDim = 'ROWS'

    val = [""] * len(COLUMNS)
    for k,v in kwargs.items():
        if k in COLUMNS:
            val[COLUMNS[k]] = v
        else:
            print('Unsupported entry member: %s, %s' % (k, repr(v)))
    vals = {'range': rangeName,
            'majorDimension': majorDim,
            'values': [val]}
    return vals

def write_book(**kwargs):
    body = build_body(**kwargs)
    service = get_service()
    result = service.spreadsheets() \
                    .values() \
                    .append(
                        spreadsheetId = SHEET_ID, 
                        range = body['range'], 
                        valueInputOption = 'USER_ENTERED',
                        insertDataOption = 'INSERT_ROWS',
                        body = body) \
                    .execute()
    return result

def sort_ddc():
    # sortSpecs = [{'dimensionIndex': COLUMNS[dim], 'sortOrder': 'ASCENDING'} for dim in SORT_BY]
    sortRange = {'sheetId': SHEET_NUMBER, 'startRowIndex': int(STARTING_CELL[1]), 'startColumnIndex':STARTING_CELL[0]}
    sortSpecs = [{'dimensionIndex':6, 'sortOrder':'ASCENDING'},{'dimensionIndex':1, 'sortOrder':'ASCENDING'},{'dimensionIndex':0, 'sortOrder':'ASCENDING'}]
    body = {'sortRange': {'range': sortRange,#'Sheet%d!%s' % (SHEET_NUMBER, STARTING_CELL),
            'sortSpecs': sortSpecs}}
    service = get_service()
    result = service.spreadsheets().values().batchUpdate(spreadsheetId = SHEET_ID, body=body).execute()
    return result


