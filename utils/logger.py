from os.path import join
import logging

from .path_handler import generate_files_path

class OnlyErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR

BASE_LEVEL_LOGGING = logging.DEBUG # El nivel mínimo a mostrar en consola
BASE_PATH_LOGS = "logs"
FILE_ERROR_LOGS = join(BASE_PATH_LOGS, "errors.log")
FILE_CRITICAL_LOGS = join(BASE_PATH_LOGS, "criticals.log")

generate_files_path(BASE_PATH_LOGS)

logging.basicConfig(level=BASE_LEVEL_LOGGING)
logger = logging.getLogger(__name__)

# Para evitar información duplicada en consola.
logger.propagate = False

# Para los mensajes en consola.
shell_handler = logging.StreamHandler()

# Para los errores facilmente evitables.
file_error_handler = logging.FileHandler(FILE_ERROR_LOGS, mode="a", encoding="utf-8")

# Para los errores más inesperados.
file_critical_handler = logging.FileHandler(FILE_CRITICAL_LOGS, mode="a", encoding="utf-8")

# Estableciendo niveles.
shell_handler.setLevel(BASE_LEVEL_LOGGING)
file_error_handler.setLevel(logging.ERROR)
file_critical_handler.setLevel(logging.CRITICAL)

# Los formatos a escribir y a mostrar.
# En este caso son iguales, pero podrían no serlo.
shell_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_error_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_critical_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Estableciendo los formatos de los handlers.
shell_handler.setFormatter(shell_format)
file_error_handler.setFormatter(file_error_format)
file_critical_handler.setFormatter(file_critical_format)

# Filtrando valores criticos, dejando solo "Error".
only_error_filter = OnlyErrorFilter()
file_error_handler.addFilter(only_error_filter)

# Añadiendo los handlers al logger.
logger.addHandler(shell_handler)
logger.addHandler(file_error_handler)
logger.addHandler(file_critical_handler)