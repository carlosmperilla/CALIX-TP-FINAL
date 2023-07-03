from os import rename
from os.path import exists, splitext, join
from uuid import uuid4

from .logger import logger
from .path_handler import generate_files_path

def backup_old_file(file_name: str, file_path: str, older_files_path: str) -> None:
    """
        Genera respaldo del archivo previo, si este ya fue escrito.
        - Lo renombra con un codigo único.
        - Lo mueve a la carpeta de old-versions.
    """

    if exists(file_path):
        base_name, file_extension = splitext(file_name)
        new_file_name = base_name + ' - ' + uuid4().hex + file_extension
        generate_files_path(older_files_path)
        rename(file_path, join(older_files_path, new_file_name))
        logger.info(f"Se ha respaldado la vieja versión como: {new_file_name}")


def write_file(file_path: str, content: bytes) -> bool:
    """
        Escribe un archivo.
        - Si es exitosa la escritura retorna True
        - Si falla, guarda en logs la exceptción y reforna False.
    """

    try:
        with open(file_path, "wb") as file:
            file.write(content)
    except Exception as e:
        logger.error(f"Un error ha ocurrido al intentar escribir el archivo: {e}")
        return False
    else:
        return True