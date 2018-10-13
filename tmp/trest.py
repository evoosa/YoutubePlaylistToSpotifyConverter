# -*- coding: utf-8 -*-
#
# from youtube_utils import YoutubePlaylistManager
# from utils import get_logger
#
# plurl = "https://www.youtube.com/watch?v=R9Fv4nW0KaM&start_radio=1&list=RDR9Fv4nW0KaM"
# loc = "c:/users/evoosa/desktop/poop"
# y = YoutubePlaylistManager(plurl, get_logger(loc))
#
# y.create_playlist_metadata_csv(loc)


import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2

SPOTIFY_CLIENT_ID = "a6d1ab65a9e249c58e5fd10285781d5a"
SPOTIFY_CLIENT_SECRET = "958aba88060d48269c726cbf3c1627b7"
SPOTIFY_REDIRECT_URI = "http://example.com/callback/"
SPOTIFY_SCOPE = "playlist-modify-private"

username = 'evoosa'

token = util.prompt_for_user_token(username,scope=scopes,client_id=client_id,client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

# token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)
