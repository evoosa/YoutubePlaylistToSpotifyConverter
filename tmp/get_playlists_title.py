# Sample Python code for user authorization

import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = "youtube_client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtubepartner']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


if __name__ == '__main__':

    service = get_authenticated_service()
    plid = 'PLVy1DVBAXDhyOuJDSwV8pMjSDnk0yMoBn'

    ### gets: a dict of dicts. the playlists title
    print(service.playlists().list(
        part='snippet,contentDetails',
        id=plid,
        fields='items(snippet(title))'
    ).execute())
