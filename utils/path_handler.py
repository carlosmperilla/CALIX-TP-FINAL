from os import mkdir
from os.path import isdir

def generate_files_path(files_path: str) -> None:
    """
        Si no existe el directorio lo crea.
    """
    if not isdir(files_path):
        mkdir(files_path)