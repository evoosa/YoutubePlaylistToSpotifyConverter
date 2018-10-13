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
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    service = get_authenticated_service()
    plid = 'PLVy1DVBAXDhyOuJDSwV8pMjSDnk0yMoBn'
    ### gets: a dict of dicts. all playlist's videos and their: title, id
    print(service.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=plid,
        fields='items(contentDetails(videoId),snippet(title))'
    ).execute())

    print('###################################################################')

    ### gets: a dict of dicts. the playlists title
    print(service.playlist().list(
        part='snippet,contentDetails',
        id=plid,
        fields='items(snippet(title))'
    ).execute())


def get_pl_video_ids(service):
    """
    Get all playlist's videos IDs
    :return: a list, containing all the playlist's videos IDs
    """
    ret_dict = service.playlistItems().list(
        part='snippet,contentDetails',
        id="RD_AWIqXzvX-U",
        fields='items(contentDetails(videoId))'
    ).execute()
    return [ret_dict['items'][i]['contentDetails']['videoId'] for i in range(len(ret_dict['items']))]


