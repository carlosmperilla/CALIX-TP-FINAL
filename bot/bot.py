from os.path import join
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

from .constants import (
                        FIRST_LOAD_TIMEOUT,
                        BASE_URL,
                        MAIN_TEXT,
                        DATASET_HEADER_LINK_XPATH,
                        DATASET_SEARCH_XPATH,
                        DATASET_LINK_XPATH,
                        DATASET_FILE_LINK_XPATH,
                        FILES_PATH,
                        OLDER_FILES_PATH,
                        FILE_TYPE
                        )

from utils.logger import logger
from utils.data_downloader import requests_and_write


class Bot:

    EXPECTED_CONDITIONS =  {
            "presence" : EC.presence_of_element_located,
            "visibility" : EC.visibility_of_element_located
        }

    @staticmethod
    def download_file(url_file: str) -> Tuple[bool, str]:
        """
            Descarga el archivo y retorna si fue exitosó o no.
        """
        logger.info("Se esta realizando la petición y escritura del archivo...")

        # Obtiene el archivo por medio de una petición y lo escribe en el disco.
        is_success, file_name = requests_and_write(
                            url_file=url_file,
                            files_path=FILES_PATH,
                            older_files_path=OLDER_FILES_PATH
                        )
        if is_success:
            logger.info("¡Archivo descargado correctamente!")
        
        return is_success, file_name
    
    @staticmethod
    def process_file(file_name):
        file_path = join(FILES_PATH, file_name)
        if FILE_TYPE == "CSV":
            c1 = "automotor_anio_modelo > 2015"
            c2 = "registro_seccional_provincia == 'Formosa'"
            c3 = "automotor_origen == 'Nacional'"

            c1b = "registro_seccional_codigo == 1216"
            c2b = "automotor_origen == 'Importado'"
            
            df = pd.read_csv(file_path, dtype={"automotor_tipo_codigo": object})
            
            print(df.query(f"{c1} and {c2} and {c3}"))
            print(df.query(f"{c1b} and {c2b}"))

    def __init__(self):
        self.driver_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.driver_options)

    def run(self):
        url_file = self.selenium_scrapping()
        was_downloaded, file_name = self.download_file(url_file)
        if was_downloaded:
            logger.info(f"Procesando archivo: {file_name}")
            self.process_file(file_name)
        else:
            logger.error("El archivo no fue descargado.")

    def selenium_scrapping(self) -> str:
        """
            Realiza el flujo de scrapping con selenium.
            Retorna la url del archivo a descargar.
        """   
        self.driver.get(BASE_URL)

        self.click_dataset_header()
        self.send_keys_search_dataset()
        self.click_dataset_link()
        url_file = self.get_url_file_dataset()     
        
        self.driver.quit()

        return url_file

    def click_dataset_header(self):
        """
            Click en el link de dataset del encabezado.
        """
        dataset_header_link_element = self.get_element_by_xpath(DATASET_HEADER_LINK_XPATH)
        dataset_header_link_element.click()

    def send_keys_search_dataset(self):
        """
            Busqueda del termino principal en el panel de busqueda.
        """
        dataset_search_element = self.get_element_by_xpath(DATASET_SEARCH_XPATH, type_condition="visibility")
        dataset_search_element.send_keys(MAIN_TEXT + Keys.ENTER)

    def click_dataset_link(self):
        """
            Click en el bloque de dataset del termino principal.
        """
        dataset_link_element = self.get_element_by_xpath(DATASET_LINK_XPATH, type_condition="visibility")
        dataset_link_element.click()

    def get_url_file_dataset(self) -> str:
        """
            Obtención de la url del archivo a descargar.
        """
        dataset_file_link_element = self.get_element_by_xpath(DATASET_FILE_LINK_XPATH)
        return dataset_file_link_element.get_attribute("href")

    def get_element_by_xpath(
            self,
            xpath: str, 
            timeout: int = FIRST_LOAD_TIMEOUT,
            type_condition: str = "presence") -> WebDriverWait:
        """
            Obtiene y retorna el elemento por xpath.
            Respetando los tiempos de carga.
            - Por defecto retorna solo si el elemento esta presente.
            - La opción "visibility" es más restrictiva requiere que el elemento sea visible.
        """
        expected_condition = self.EXPECTED_CONDITIONS.get(type_condition)

        return WebDriverWait(self.driver, timeout).until(
            expected_condition((By.XPATH, xpath))
        )