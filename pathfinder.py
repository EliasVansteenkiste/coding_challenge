"""Checks if all datapaths and files exist"""
import json
import utils
import os



with open('SETTINGS.json') as data_file:
    paths = json.load(data_file)

CONTOURS_PATH = paths["CONTOURS_PATH"]
utils.check_data_paths(CONTOURS_PATH)

DICOMS_PATH = paths["DICOMS_PATH"]
utils.check_data_paths(DICOMS_PATH)

LINK_PATH = paths["LINK_PATH"]
if not os.path.isfile(LINK_PATH):
    raise ValueError('Could not find a link CSV file')