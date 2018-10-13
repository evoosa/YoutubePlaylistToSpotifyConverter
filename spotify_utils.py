# -*- coding: utf-8 -*-

from typing import List
from spotipy import Spotify, util
from utils import get_unpanctuated_str
from csv import DictReader
from time import sleep

SPOTIFY_CLIENT_ID = "a6d1ab65a9e249c58e5fd10285781d5a"
SPOTIFY_CLIENT_SECRET = "958aba88060d48269c726cbf3c1627b7"
SPOTIFY_REDIRECT_URI = "http://example.com/callback/"
SPOTIFY_SCOPE = "playlist-modify-private playlist-modify-public"
SPOTIFY_USERNAME = "21afga6ttyuj4sqj772aapb3q"

SEARCH_LIMIT = 1

# Strings
PLAYLIST_EXISTS_ERROR = "playlist already exists!"


class SpotifyManager(object):
    """
    Spotify Management Utilities
    """

    def __init__(self, logger):
        self._logger = logger
        self.redirect_uri: str = SPOTIFY_REDIRECT_URI
        self.client_id: str = SPOTIFY_CLIENT_ID
        self.client_secret: str = SPOTIFY_CLIENT_SECRET
        self.scope: str = SPOTIFY_SCOPE
        self._spotify_obj = self._create_spotify_obj()

    def _create_spotify_obj(self):
        """
        Authenticate against spotify,
        :return: authenticated spotipy.Spotify object
        """
        self._logger.debug("initializing a spotipy Object")
        try:
            token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=SPOTIFY_SCOPE, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI)
            return Spotify(auth=token)
        except Exception as e:
            self._logger.exception("FAILURE - failed to initialize a spotipy object")
            raise

    def user_playlist_exists(self, pl_name) -> bool:
        """
        Checks if a playlist named pl_name exists in the user's playlists
        :param pl_name: playlist name
        :return: True is playlist exists, False if not
        """
        self._logger.debug("checking if the playlist: '{pl_name}' already exists in the user's: '{username}' playlists".format(pl_name=pl_name, username=SPOTIFY_USERNAME))
        try:
            user_pls = self._spotify_obj.user_playlists(SPOTIFY_USERNAME)
            user_playlists = [user_pls["items"][i]["name"] for i in range(len(user_pls["items"]))]
        except Exception as e:
            self._logger.exception("can't retrieve user's: '{username}' playlists!".format(username=SPOTIFY_USERNAME))
            raise

        if pl_name in user_playlists:
            self._logger.error("playlist name '{pl_name}' already exists!".format(pl_name=pl_name))
            return True
        self._logger.debug("playlist name '{pl_name}' doesn't exist - continuing".format(pl_name=pl_name))
        return False

    def create_playlist(self, pl_name):
        """
        Creates a playlist in spotify with the given pl_name
        :param pl_name: playlist name
        :return: the playlist's ID
        """
        sleep_time = 2
        if not self.user_playlist_exists(pl_name):
            try:
                self._logger.debug("trying to create the playlist: '{pl_name}' for user: '{username}'".format(pl_name=pl_name, username=SPOTIFY_USERNAME))
                pl_obj = self._spotify_obj.user_playlist_create(SPOTIFY_USERNAME, pl_name)
                self._logger.info("created spotify playlist: '{pl_name}' for user: '{username}'".format(pl_name=pl_name, username=SPOTIFY_USERNAME))
                sleep(sleep_time)
                return pl_obj['id']
            except Exception as e:
                self._logger.exception("can't create playlist: '{pl_name}' for the user: '{username}'".format(pl_name=pl_name, username=SPOTIFY_USERNAME))
                raise
        else:
            self._logger.error("{} exiting!".format(PLAYLIST_EXISTS_ERROR))
            raise ValueError(PLAYLIST_EXISTS_ERROR)

    def delete_playlist(self, pl_id):
        """
        Deletes a playlist from a given user account, with the given pl_id
        :param pl_id: playlist's ID
        """
        try:
            self._spotify_obj.user_playlist_unfollow(SPOTIFY_USERNAME, pl_id)
        except Exception as e:
            self._logger.exception("FAILURE - can't delete the playlist with ID: {pl_id}".format(pl_id=pl_id))
            pass

    def add_track_to_playlist(self, track_id: str, pl_id: str):
        """
        Adds a track to a user's playlist, by the track's ID
        :param track_id: track ID in spotify
        :param pl_id: playlist ID
        """
        try:
            self._logger.debug("adding track with ID: '{track_id}'".format(track_id=track_id))
            self._spotify_obj.user_playlist_add_tracks(SPOTIFY_USERNAME, pl_id, [track_id])
        except Exception as e:
            self._logger.exception("FAILURE - can't add track with ID: '{track_id}'".format(track_id=track_id))
            pass

    def _get_valid_title(self, title: str) -> str:
        """
        Remove punctuation, lower, and remove invalid words from the title
        :param title: title string
        :return: a valid title, string
        """
        self._logger.debug("parsing song's title: '{title}'".format(title=title))
        title = get_unpanctuated_str(title).lower()
        forbidden_words = ['radio edit', 'original mix', 'audio', 'official', 'music video', 'featuring', 'video', 'feat', 'feat.', 'official music video', 'and', 'ft', 'ft.']
        for forbidden_word in forbidden_words: title = title.replace(forbidden_word, '')
        self._logger.debug("finished parsing title: '{title}'".format(title=title))
        return title

    def get_track_id_by_title(self, title: str) -> str:
        """
        Search a song by a given string, and get the first result
        If it fails, return None
        :param title: string to search
        :return: a song ID string
        """
        query = '{title}'.format(title=self._get_valid_title(title))
        try:
            self._logger.debug("getting track ID by title: '{title}'".format(title=query))
            result = self._spotify_obj.search(q=query, type="track", limit=SEARCH_LIMIT)
            return result['tracks']['items'][0]['id']
        except Exception as e:
            self._logger.debug("FAILURE - wasn't able to retrieve track ID by title!")
            return None

    def get_track_id_by_track_name_and_artist(self, track_name: str, artist_name=None) -> str:
        """
        Search a song by a given artist and track name, and get the first result
        If it fails, return None
        :param artist_name: track name
        :param track_name: artist name
        :return: a song ID string, or None
        """
        none_str = ''
        if artist_name == none_str:
            self._logger.debug("getting track ID by track name: '{track_name}'".format(track_name=track_name))
            query = 'track:"{track}"'.format(track=track_name)

        elif artist_name == none_str and track_name == none_str:
            self._logger.debug("track has no artist nor track name! skipping")
            return None
        else:
            self._logger.debug("getting track ID by track name and artist: '{track_name}', '{artist_name}'".format(track_name=track_name, artist_name=artist_name))
            query = 'artist:"{artist}" track:"{track}"'.format(artist=artist_name, track=track_name)

        try:
            result = self._spotify_obj.search(q=query, type="track", limit=SEARCH_LIMIT)
            track_id = result['tracks']['items'][0]['id']
            self._logger.debug("got track ID: '{id}'".format(id=track_id))
            return track_id
        except Exception as e:
            self._logger.debug("FAILURE - wasn't able to retrieve track ID by track name and artist!")
            return None

    def add_tracks_to_playlist(self, tracks_csv_loc: str, pl_id: str):
        """
        Add tracks from a CSV file, to a playlist in spotify
        the CSV can be created with YoutubePlaylistManager.create_playlist_metadata_csv
        :param tracks_csv_loc: tracks CSV file location
        :param pl_id: playlist's ID
        """
        get_data_from_csv_error = "FAILURE - can't retrieve data from CSV!"
        tracks_ordered_dicts = []
        try:
            self._logger.debug("opening tracks data CSV file for reading: {csv_loc}".format(csv_loc=tracks_csv_loc))
            with open(tracks_csv_loc, "r", encoding='utf8') as csvfile:
                self._logger.debug("retrieving tracks data from CSV")
                reader = DictReader(csvfile)
                for track_dict in reader:
                    tracks_ordered_dicts.append(track_dict)
                self._logger.debug("done retrieving tracks data from CSV")
        except Exception as e:
            self._logger.exception(get_data_from_csv_error)
            raise

        for track_dict in tracks_ordered_dicts:
            self._logger.debug("getting track ID from spotify: {track_name}".format(track_name=track_dict['track']))
            if not track_dict['track'] == '' and not track_dict['artist'] == '':
                track_id = self.get_track_id_by_track_name_and_artist(track_dict['track'], track_dict['artist'])
                if track_id is None:
                    track_id = self.get_track_id_by_title(track_dict['title'])
            else:
                track_id = self.get_track_id_by_title(track_dict['title'])

            if track_id is None:
                self._logger.warning("can't retrieve data for track: '{title}'. skipping".format(title=track_dict['title']))
                pass
            else:
                self.add_track_to_playlist(track_id, pl_id)
                self._logger.info("successfully added track '{title}' to playlist".format(title=track_dict['title']))

        self._logger.info("FINISHED - finished adding tracks to playlist!")


# from utils import get_logger
# sp = SpotifyManager(logger=get_logger(r"c:\users\evoosa\desktop"))
# sp.create_playlist("Bob Moses - bloob")