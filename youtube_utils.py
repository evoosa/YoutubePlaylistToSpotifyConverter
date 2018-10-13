# -*- coding: utf-8 -*-

from config import ENV_ENCODING
from typing import List, Dict
import youtube_dl
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from csv import DictWriter
from os.path import join
from datetime import datetime

DEF_PL_NAME = "NoName"

# youtube API options
GOOGLE_CLIENT_ID = "220458860156-ulm6bbhcaf3v1pl35ebbr70gji8ls6hu.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "52S9gDH3al1IbIGuy_5Q4HPf"
SCOPES = ['https://www.googleapis.com/auth/youtubepartner'] # TODO - make it less violent, READ ONLY!
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

CLIENT_CONFIG = {
    "installed": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "yotospo",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://www.googleapis.com/oauth2/v3/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost"
        ]
    }
}

# youtube_dl options
YDL_OPTIONS_DICT = {'quiet': True}
NEEDED_VIDEO_METADATA_LIST: List = ['id', 'title', 'artist', 'track']

# strings
INVALID_PL_URL_FORMAT = """
FAILURE - invalid playlist URL! please enter a valid playlist URL!
playlist's URL:
{}
"""


class YoutubePlaylistManager(object):
    """
    Youtube Playlist Management Utilities
    """

    def __init__(self, pl_url, logger):
        self._logger = logger
        self._yt_api_obj = self._init_youtube_api_obj()
        self._ydl_obj = self._init_youtube_dl_obj()
        self.playlist_url: str = pl_url
        self.playlist_id: str = self.get_playlist_id()
        self.playlist_name: str = self.get_playlist_name()
        self.max_search_results = 50 # this is literally the maximum. fuck.
        self.playlist_videos_metadata = None

    @staticmethod
    def is_playlist_url_valid(pl_url):
        """
        Check fot the playlist's URL validity
        :param pl_url: playlist's URL
        :return: True / False for success / failure accordingly
        """
        if "list=" not in pl_url:
            return False
        else:
            return True

    def get_playlist_id(self):
        """
        Returns a playlist ID from it's youtube URL
        :return: the playlist's ID
        """
        self._logger.debug("getting the playlist's ID from it's URL")
        if self.is_playlist_url_valid(self.playlist_url):
            starting_str = self.playlist_url[self.playlist_url.find("list="):]
            if "&" in starting_str:
                pl_id = starting_str[5:starting_str.find("&")]
            else:
                pl_id = starting_str[5:]

            self._logger.debug("playlist's ID - '{}'".format(pl_id))
            return pl_id

        else:
            self._logger.error(INVALID_PL_URL_FORMAT)
            raise ValueError(INVALID_PL_URL_FORMAT)

    def _init_youtube_api_obj(self):
        """
        Initialize an instance of a Youtube API Object
        :return: authenticated youtube API object
        """
        self._logger.debug("initializing a youtube API object")
        try:
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            credentials = flow.run_console() # will prompt user to authenticate with google
            return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        except Exception as e:
            self._logger.exception("FAILURE - failed to initialize a youtube API object")
            raise

    def _init_youtube_dl_obj(self):
        """
        Initialize an instance of youtube_dl.YoutubeDL object
        :return: an instance of youtube_dl.YoutubeDL object
        """
        self._logger.debug("initializing a youtube_dl object")
        try:
            return youtube_dl.YoutubeDL(YDL_OPTIONS_DICT)
        except Exception as e:
            self._logger.exception("FAILURE - failed to initialize a youtube_dl object")

    def get_playlist_name(self) -> str:
        """
        Gets the playlist name from a given URL
        :return: playlist name if found. a default_val if wasn't found
        """
        self._logger.info("getting playlist's name..")
        try:
            ret_dict = self._yt_api_obj.playlists().list(
                part='snippet,contentDetails',
                id=self.playlist_id,
                fields='items(snippet(title))'
            ).execute()
        except Exception as e:
            self._logger.exception("FAILURE - could not get the playlist's name using youtube's API!")
            raise

        try:
            return ret_dict['items'][0]['snippet']['title']
        except (KeyError, IndexError) as e:
            self._logger.exception(INVALID_PL_URL_FORMAT)
            raise

    def get_playlist_videos_ids(self) -> List[str]:
        """
        Get all playlist's videos IDs
        :return: a list, containing all the playlist's videos IDs
        """
        id_list = []
        self._logger.info("getting playlist's videos IDs..")
        next_page_token = None
        while True:
            try:
                self._logger.debug("trying to retrive page with the token: '{}'".format(next_page_token))
                ret_dict = self._yt_api_obj.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=self.playlist_id,
                    maxResults=self.max_search_results,
                    fields='nextPageToken,items(contentDetails(videoId))',
                    pageToken=next_page_token
                ).execute()
                id_list += [ret_dict['items'][i]['contentDetails']['videoId'] for i in range(len(ret_dict['items']))]
            except Exception as e:
                self._logger.exception("FAILURE - could not get the playlist's videos IDs with the youtube API!")
                raise
            try:
                next_page_token = ret_dict['nextPageToken']
            except KeyError:
                return id_list

    def _get_video_metadata(self, video_id: str) -> Dict:
        """
        Gets a dict, containing a video's metadata.
        the metadata that will be retrieved is decided by the NEEDED_VIDEO_METADATA variable
        for example:
        { 'id': '123', 'title': 'lol', 'artist': 'poop'}
        :param video_id: the video's ID
        :return: a dict conatining the video's metadata
        """
        video_url = 'https://www.youtube.com/watch?v=' + video_id
        with self._ydl_obj as ydl:
            video_metadata = ydl.extract_info(video_url, download=False)
            return {key: video_metadata[key] for key in NEEDED_VIDEO_METADATA_LIST}

    def get_all_videos_metadata(self) -> List[Dict[str, str]]:
        """
        Gets a list with a metadata dict entry for each video in the playlist
        [ {video's metadata dict}, {video's metadata dict} ... ]
        :return: a list with all videos metadata dicts
        """
        vids_metadata_list = []
        videos_ids = self.get_playlist_videos_ids()
        self._logger.info("collecting all videos metadata..")
        for i in range(len(videos_ids)):
            try:
                self._logger.info("collecting metadata for video with ID: '{}'".format(videos_ids[i]))
                vids_metadata_list.append(self._get_video_metadata(video_id=videos_ids[i]))
                self._logger.debug("SUCCESS - got metadata for video with ID: '{}'".format(videos_ids[i]))
            except Exception as e:
                self._logger.exception("FAILURE - could not get information for video with ID: '{}'".format(videos_ids[i]))
        self.playlist_videos_metadata = vids_metadata_list
        self._logger.info("success - finished collecting information about the videos in the playlist")

    def create_playlist_metadata_csv(self, csv_directory: str) -> str:
        """
        Creates a CSV file, with all the playlist's videos metadata
        :param csv_directory: the directory to puth the CSV file in
        :return: CSV full path
        """
        csv_filename = self.playlist_name.replace(" ", "_") + '-' + str(datetime.now().date()) + '-' + str(datetime.now().time()).split(".")[0].replace(":", "-") + ".csv"
        csv_full_path = join(csv_directory, csv_filename)
        self._logger.info("creating CSV playlist info file - '{}'".format(csv_full_path))
        try:
            with open(csv_full_path, 'w', newline='', encoding=ENV_ENCODING) as csvfile:
                writer = DictWriter(csvfile, fieldnames=NEEDED_VIDEO_METADATA_LIST)
                writer.writeheader()
                for i in range(len(self.playlist_videos_metadata)):
                    self._logger.debug("writing row to CSV file - {}".format(str(self.playlist_videos_metadata[i]).encode(ENV_ENCODING)))
                    writer.writerow(self.playlist_videos_metadata[i])
            return csv_full_path
        except Exception as e:
            self._logger.exception("FAILURE - failed to create CSV file")
            raise
