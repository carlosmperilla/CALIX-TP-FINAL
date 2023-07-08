from .bots.selenium_scrapping import SeleniumScrapping

from utils.logger import logger

from .bots.download_file import DownloadFile
from .bots.process_file import ProcessFile

from time import time
class Bot(SeleniumScrapping):
    
    def run(self):
        url_file = super().run()
        
        was_downloaded, file_name = DownloadFile(url_file=url_file).run()

        if was_downloaded:
            # ProcessFile internamente se comunica con SendData
            # Para procesar y enviar la información.
            logger.info(f"Procesando archivo: {file_name}")
            a = time()
            ProcessFile(file_name).run()
            b = time()
            logger.info(f"Tiempo ejecución {b-a}")
        else:
            logger.error("El archivo no fue descargado.")