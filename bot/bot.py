from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .constants import (
                        FIRST_LOAD_TIMEOUT,
                        BASE_URL,
                        MAIN_TEXT,
                        DATASET_HEADER_LINK_XPATH,
                        DATASET_SEARCH_XPATH,
                        DATASET_LINK_XPATH,
                        DATASET_FILE_LINK_XPATH,
                        FILES_PATH,
                        OLDER_FILES_PATH
                        )

from utils.logger import logger
from utils.data_downloader import requests_and_write


def get_element_by_xpath(
        driver: webdriver.Chrome, 
        xpath: str, 
        timeout: int = FIRST_LOAD_TIMEOUT, 
        type_condition: str = "presence") -> WebDriverWait:
    """
        Obtiene y retorna el elemento por xpath.
        Respetando los tiempos de carga.
        - Por defecto retorna solo si el elemento esta presente.
        - La opción "visibility" es más restrictiva requiere que el elemento sea visible.
    """
    
    expected_condition = {
        "presence" : EC.presence_of_element_located,
        "visibility" : EC.visibility_of_element_located
    }.get(type_condition)

    return WebDriverWait(driver, timeout).until(
        expected_condition((By.XPATH, xpath))
    )


def run() -> bool:
    """
        Corre el codigo principal del BOT.
        - Retorna True si el funcionamiento fue el esperado, False en caso contrario.
    """

    options = webdriver.ChromeOptions()
    url_file = ""
    
    with webdriver.Chrome(options=options) as driver:
        
        driver.get(BASE_URL)

        # Click en el link de dataset del encabezado.
        dataset_header_link_element = get_element_by_xpath(driver, DATASET_HEADER_LINK_XPATH)
        dataset_header_link_element.click()

        # Busqueda del termino principal en el panel de busqueda.
        dataset_search_element = get_element_by_xpath(driver, DATASET_SEARCH_XPATH, type_condition="visibility")
        dataset_search_element.send_keys(MAIN_TEXT + Keys.ENTER)

        # Click en el bloque de dataset del termino principal.
        dataset_link_element = get_element_by_xpath(driver, DATASET_LINK_XPATH, type_condition="visibility")
        dataset_link_element.click()

        # Obtención de la url del archivo a descargar.
        dataset_file_link_element = get_element_by_xpath(driver, DATASET_FILE_LINK_XPATH)
        url_file = dataset_file_link_element.get_attribute("href")
    
    logger.info("Se esta realizando la petición y escritura del archivo...")

    # Obtiene el archivo por medio de una petición y lo escribe en el disco.
    is_success = requests_and_write(
                        url_file=url_file,
                        files_path=FILES_PATH,
                        older_files_path=OLDER_FILES_PATH
                    )
    if is_success:
        logger.info("¡Archivo descargado correctamente!")
    
    return is_success