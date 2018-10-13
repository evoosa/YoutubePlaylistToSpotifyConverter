# imports
import spotify_utils
from spotify_utils import SpotifyManager
from youtube_utils import YoutubePlaylistManager, INVALID_PL_URL_FORMAT
from os.path import join, exists
from os import mkdir
from sys import platform
from utils import get_logger, get_output_dir_from_user
from sys import exit

# default output location, determined by the OS
default_output_dir_name = "yospo"
if platform == "win32":
    default_output_location = "c:/temp/"
elif "linux" in platform:
    default_output_location = "/tmp/"
else:
    raise EnvironmentError("YoSpo supports Windows and Linux platforms only!")

# get the output directory from the user
output_dir = get_output_dir_from_user(default_loc=default_output_location)
output_path = join(output_dir, default_output_dir_name)

# if the directory doesn't exist, create it
if not exists(output_path):
    mkdir(output_path)

# create a logger instance
logger = get_logger(output_path)
logger.debug("initialized a logger instance")
logger.debug("running on a '{platform}' platform".format(platform=platform))

# ask for playlist url
pl_url = input("Enter a Youtube Playlist's URL to Transfer: ")
logger.debug("running on playlist with the URL : '{pl_url}'".format(pl_url=pl_url))

# check if the URL is valid before proceeding
logger.debug("checking if playlist's URL is valid..")
if not YoutubePlaylistManager.is_playlist_url_valid(pl_url):
    logger.error(INVALID_PL_URL_FORMAT)
    exit(1)
else:
    logger.debug("success - playlist's URL passed validity check")


# initialize a SpotifyManager object
spotify_manager = SpotifyManager(logger)
logger.debug("creating a SpotifyManager instance..")
try:
    spotify_manager = SpotifyManager(logger=logger)
except Exception as e:
    logger.exception("failed to initiate a SpotifyManager instance!")
    raise

# initialize a YoutubePlaylistManager object
logger.debug("creating a YoutubeManager instance..")
try:
    youtube_manager = YoutubePlaylistManager(pl_url=pl_url, logger=logger)
except Exception as e:
    logger.exception("failed to initiate a YoutubeManager instance!")
    raise

# get all playlist's videos metadata from youtube
youtube_manager.get_all_videos_metadata()

# create the CSV file, containing all the videos metadata information
track_data_csv_full_path = youtube_manager.create_playlist_metadata_csv(csv_directory=output_path)

# create the playlist in spotify
spotify_pl_id = spotify_manager.create_playlist(youtube_manager.playlist_name)

# add tracks from youtube playlist, to the spotify playlist
try:
    spotify_manager.add_tracks_to_playlist(track_data_csv_full_path, spotify_pl_id)
except:
    logger.exception("FAILURE - can't add tracks to playlist!")
    spotify_manager.delete_playlist(spotify_pl_id)

print(
"""
~ Track Data CSV File Location: '{csv_loc}'

~ Log Location: '{log_loc}'

~ New Playlist's Name: '{pl_name}'
""".format(csv_loc=track_data_csv_full_path, log_loc=output_path, pl_name=youtube_manager.playlist_name))
