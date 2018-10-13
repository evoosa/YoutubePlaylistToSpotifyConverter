from bottle import route, run, request
import spotipy
from spotipy import oauth2

PORT_NUMBER = 8080
CACHE = '.spotipyoauthcache'

SPOTIPY_CLIENT_ID = "a6d1ab65a9e249c58e5fd10285781d5a"
SPOTIPY_CLIENT_SECRET = "958aba88060d48269c726cbf3c1627b7"
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = "playlist-modify-private playlist-modify-public"
#SPOTIFY_USERNAME = "21afga6ttyuj4sqj772aapb3q"

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

@route('/')
def index():

    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results

    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

run(host='', port=8080)