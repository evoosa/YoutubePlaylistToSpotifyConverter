from os.path import exists
import logging
import sys
from datetime import datetime
from os.path import join
from string import punctuation
import re


def get_output_dir_from_user(default_loc: str) -> str:
    """
    Ask the user for the output directory location (where should the location of the log and the CSV file)
    :return: output directory, only when valid
    """
    log_loc = input(
        """
Enter Path to save the output folder in
press 'Enter' for default ['{default_loc}']

Path: """.format(default_loc=default_loc)
    )
    if log_loc != '':
        if exists(log_loc):
            return log_loc
        else:
            print("\n!!! Invalid path! try again!\n")
            return get_output_dir_from_user(default_loc=default_loc)
    else:
        return default_loc


def get_logger(log_location: str):
    """
    Create a logger, and return it already configured
    :param log_location: the log's location
    :return: logging.Logger instance
    """
    # set the main logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create the log full filename
    log_filename = "yospo-" + str(datetime.now().date()) + '-' + str(datetime.now().time()).split(".")[0].replace(":", "-") + ".log"
    log_full_path = join(log_location, log_filename)

    # create log file handler
    log_handler = logging.FileHandler(filename=log_full_path)
    log_handler.setLevel(logging.DEBUG)

    # create console logging handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)

    # create logging formats
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # set handlers with the formatters
    console_handler.setFormatter(console_formatter)
    log_handler.setFormatter(log_formatter)

    # add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(log_handler)

    return logger

def get_unpanctuated_str(string: str) -> str:
    """
    Removes Punctuation characters from a string
    :param string: string
    :return: string without punctuation
    """
    exclude_chars = set(punctuation)
    string = ''.join(ch for ch in string if ch not in exclude_chars)
    # remove all non-ASCII characters, replace them with a space - ' '
    string = re.sub(r'[^\x00-\x7F]+', ' ', string)
    return string

