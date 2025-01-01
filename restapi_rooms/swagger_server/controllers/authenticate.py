import os
from google.oauth2 import service_account
from googleapiclient.discovery import build




def authenticate():
    """ Authentication with service account
    """

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'creds.json'
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    
    return credentials

def get_calendar_service():
    credentials = authenticate()
    service = build('calendar', 'v3', credentials=credentials)
    return service
