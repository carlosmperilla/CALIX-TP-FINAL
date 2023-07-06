from os import rename
from os.path import join, exists, splitext
from typing import Tuple
from uuid import uuid4

from requests import get

from .constants import (
                        FILES_PATH,
                        OLDER_FILES_PATH
                        )

from utils.logger import logger
from utils.path_handler import generate_files_path


class DownloadFile:

    FILES_PATH = FILES_PATH
    OLDER_FILES_PATH = OLDER_FILES_PATH

    def __init__(self, url_file: str):
        self.url_file = url_file
        self.file_name = self.url_file.split('/')[-1]
        self.file_path = join(self.FILES_PATH, self.file_name)


    def backup_old_file(self) -> None:
        """
            Genera respaldo del archivo previo, si este ya fue escrito.
            - Lo renombra con un codigo único.
            - Lo mueve a la carpeta de old-versions.
        """

        if exists(self.file_path):
            base_name, file_extension = splitext(self.file_name)
            new_file_name = base_name + ' - ' + uuid4().hex + file_extension
            generate_files_path(self.OLDER_FILES_PATH)
            rename(self.file_path, join(self.OLDER_FILES_PATH, new_file_name))
            logger.info(f"Se ha respaldado la vieja versión como: {new_file_name}")


    def write_file(self, content: bytes) -> bool:
        """
            Escribe un archivo.
            - Si es exitosa la escritura retorna True
            - Si falla, guarda en logs la exceptción y reforna False.
        """

        try:
            with open(self.file_path, "wb") as file:
                file.write(content)
        except Exception as e:
            logger.error(f"Un error ha ocurrido al intentar escribir el archivo: {e}")
            return False
        else:
            return True


    def requests_and_write(self) -> Tuple[bool, str]:
        """
            A partir de una petición reescribe un archivo de forma segura.
            - Las versiones viejas son respaldadas.
            - Retorna True si el funcionamiento fue el esperado.
            - Retorna False si hubo un error en el archivo o el funcionamiento no fue   
            el esperado.
            - Se guarda en logs si el fallo fue por un status_code fallido.
        """
            
        file_request = get(self.url_file)
        is_success = False
        if file_request.status_code == 200:
            generate_files_path(self.FILES_PATH)
            self.backup_old_file()
            is_success = self.write_file(file_request.content)
        else:
            logger.error(f"Request incorrecto - status: {file_request.status_code}")
        return is_success, self.file_name


    def run(self) -> Tuple[bool, str]:
        """
            Descarga el archivo y retorna si fue exitosó o no.
        """
        logger.info("Se esta realizando la petición y escritura del archivo...")

        # Obtiene el archivo por medio de una petición y lo escribe en el disco.
        is_success, file_name = self.requests_and_write()
        if is_success:
            logger.info("¡Archivo descargado correctamente!")
        
        return is_success, file_name
