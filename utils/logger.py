from os.path import join
import logging
import logging.config

from .path_handler import generate_files_path

class OnlyErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR

BASE_PATH_LOGS = "logs"
CONFIG_FILE = join("config", "logging.ini")

generate_files_path(BASE_PATH_LOGS)

# Usamos un archivo de configuración.
logging.config.fileConfig(CONFIG_FILE)

# Nombramos el logger global.
logger = logging.getLogger('globalLogger')

# Le añadimos un filtro al manejador de errores.
for handler in logger.handlers:
    if handler.level == logging.ERROR:
        filter = OnlyErrorFilter()
        handler.addFilter(filter)