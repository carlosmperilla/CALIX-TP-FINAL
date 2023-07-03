from os.path import join

from decouple import Config, RepositoryIni

config = Config(RepositoryIni("config/bot-settings.ini"))

FIRST_LOAD_TIMEOUT = config("FIRST_LOAD_TIMEOUT", default=10, cast=int)
BASE_URL = config("BASE_URL")
MAIN_TEXT = config("MAIN_TEXT")
FILE_TYPE = config("FILE_TYPE")

DATASET_HEADER_LINK_XPATH = config("DATASET_HEADER_LINK_XPATH")
DATASET_SEARCH_XPATH = config("DATASET_SEARCH_XPATH")
DATASET_LINK_XPATH = config("DATASET_LINK_XPATH").format(MAIN_TEXT)

DATASET_LAST_DATE_XPATH = config("DATASET_LAST_DATE_XPATH")
DATASET_FILE_LINK_AXIS = config("DATASET_FILE_LINK_AXIS").format(FILE_TYPE.lower())
DATASET_FILE_LINK_XPATH = DATASET_LAST_DATE_XPATH + DATASET_FILE_LINK_AXIS

FILES_PATH = config("FILES_PATH")
OLDER_FILES_PATH = join(FILES_PATH, "old-versions")