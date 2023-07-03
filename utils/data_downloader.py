from os.path import join
from typing import Tuple

from requests import get

from .logger import logger

from .file_handler import (
                            generate_files_path,
                            backup_old_file,
                            write_file
                            )


def requests_and_write(url_file: str, files_path: str, older_files_path: str) -> Tuple[bool, str]:
    """
        A partir de una petición reescribe un archivo de forma segura.
        - Las versiones viejas son respaldadas.
        - Retorna True si el funcionamiento fue el esperado.
        - Retorna False si hubo un error en el archivo o el funcionamiento no fue   
        el esperado.
        - Se guarda en logs si el fallo fue por un status_code fallido.
    """
        
    file_request = get(url_file)
    is_success = False
    file_name = ""
    if file_request.status_code == 200:
        file_name = url_file.split('/')[-1]
        file_path = join(files_path, file_name)
        generate_files_path(files_path)
        backup_old_file(file_name, file_path, older_files_path)
        is_success = write_file(file_path, file_request.content)
    else:
        logger.error(f"Request incorrecto - status: {file_request.status_code}")
    return is_success, file_name