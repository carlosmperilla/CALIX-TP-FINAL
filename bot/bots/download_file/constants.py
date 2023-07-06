from os.path import join

from decouple import Config, RepositoryIni

config = Config(RepositoryIni("config/bot-settings.ini"))

FILES_PATH = config("FILES_PATH")
OLDER_FILES_PATH = join(FILES_PATH, "old-versions")