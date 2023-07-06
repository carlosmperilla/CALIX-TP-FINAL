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
                        DATASET_FILE_LINK_XPATH
                        )


class SeleniumScrapping:

    BASE_URL = BASE_URL
    MAIN_TEXT = MAIN_TEXT
    DATASET_HEADER_LINK_XPATH = DATASET_HEADER_LINK_XPATH
    DATASET_SEARCH_XPATH = DATASET_SEARCH_XPATH
    DATASET_LINK_XPATH = DATASET_LINK_XPATH
    DATASET_FILE_LINK_XPATH = DATASET_FILE_LINK_XPATH
    EXPECTED_CONDITIONS =  {
            "presence" : EC.presence_of_element_located,
            "visibility" : EC.visibility_of_element_located
    }

    def __init__(self):
        self.driver_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.driver_options)

    def run(self):
        """
            Carga selenium y realiza las acciones principales del scraping.
        """
        url_file = self.steps()
        return url_file

    def steps(self) -> str:
        """
            Realiza el flujo de scrapping con selenium.
            Retorna la url del archivo a descargar.
        """   
        self.driver.get(self.BASE_URL)

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
        dataset_header_link_element = self.get_element_by_xpath(self.DATASET_HEADER_LINK_XPATH)
        dataset_header_link_element.click()

    def send_keys_search_dataset(self):
        """
            Busqueda del termino principal en el panel de busqueda.
        """
        dataset_search_element = self.get_element_by_xpath(self.DATASET_SEARCH_XPATH, type_condition="visibility")
        dataset_search_element.send_keys(self.MAIN_TEXT + Keys.ENTER)

    def click_dataset_link(self):
        """
            Click en el bloque de dataset del termino principal.
        """
        dataset_link_element = self.get_element_by_xpath(self.DATASET_LINK_XPATH, type_condition="visibility")
        dataset_link_element.click()

    def get_url_file_dataset(self) -> str:
        """
            Obtención de la url del archivo a descargar.
        """
        dataset_file_link_element = self.get_element_by_xpath(self.DATASET_FILE_LINK_XPATH)
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