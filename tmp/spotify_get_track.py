from spotipy import Spotify, util

SPOTIFY_CLIENT_ID = "a6d1ab65a9e249c58e5fd10285781d5a"
SPOTIFY_CLIENT_SECRET = "958aba88060d48269c726cbf3c1627b7"
SPOTIFY_REDIRECT_URI = "http://example.com/callback/"
SPOTIFY_SCOPE = "playlist-modify-private playlist-modify-public"
SPOTIFY_USERNAME = "21afga6ttyuj4sqj772aapb3q"

token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=SPOTIFY_SCOPE, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI)
sp = Spotify(auth=token)

#q = 'artist:air track:"cherry blossom girl"'
q = 'artist:{} track:"cherry blossom girl"'

d = sp.search(q=q, type="track", limit=1)

id = d['tracks']['items'][0]['id']

lst = ['id', 'artists', 'name'] # , 'album']
