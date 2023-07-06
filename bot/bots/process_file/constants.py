from decouple import Config, RepositoryIni

config = Config(RepositoryIni("config/bot-settings.ini"))

FILES_PATH = config("FILES_PATH")
FILE_TYPE = config("FILE_TYPE")