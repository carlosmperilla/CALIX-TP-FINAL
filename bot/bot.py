from os.path import join
from typing import Tuple, List

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
            
            df = pd.read_csv(file_path, dtype={"automotor_tipo_codigo": object, "titular_domicilio_provincia_id": str})

            equivalencia = {
                "procedure": {
                    # "code_number": lambda serie: str(serie.name), # dff.iloc[0].name
                    "tramite_tipo": "type",
                    "titular_domicilio_provincia_id": "province_code"
                },
                "province": {
                    "titular_domicilio_provincia": "name",
                    "titular_domicilio_provincia_id": "code",
                    "titular_pais_nacimiento_id": "country_code"
                },
                "country": {
                    "titular_pais_nacimiento_id": "code",
                    "titular_pais_nacimiento": "name"
                }
            }
            from requests import post
            df_a = df.query(f"{c1} and {c2} and {c3}")
            df_b = df.query(f"{c1b} and {c2b}")



            def row_parse(row, table_name: str) -> dict:
                return row[equivalencia[table_name].keys()].rename(equivalencia[table_name]).to_dict()

            def send_hold_provinces(provinces_on_hold: dict):
                status_success = []
                error_messages = []
                for province_data in provinces_on_hold.values():
                    response = post(f"http://127.0.0.1:8000/provinces", json=province_data)
                    is_response_success = response.status_code == 200
                    status_success.append(is_response_success)

                    if not is_response_success:
                        error_messages.append(response.text)

                return all(status_success), error_messages
            

            def post_all_data(
                    all_data: dict,
                    codes_alredy_stored: dict, 
                    provinces_on_hold: dict
                    ) -> Tuple[bool, List[str]]:
                status_success = []
                error_messages = []
                nan_to_none = lambda value: None if pd.isna(value) else value

                for endpoint, data in all_data.items():
                    new_data = {key: nan_to_none(value) for key, value in data.items()}
                    new_data_code = new_data.get("code")
                    
                    codes_by_endpoint = codes_alredy_stored.get(endpoint)
                    has_codes_by_endpoint = codes_by_endpoint is not None
                    if has_codes_by_endpoint:
                        if new_data_code in codes_by_endpoint:
                                continue
                        
                    # mientras contry_code sea nulo se guarda, si se persiste si va el caso al final.
                    if endpoint == "provinces":

                        if new_data.get("country_code") is None:
                            provinces_on_hold[new_data_code] = new_data
                            continue
                        else:
                            provinces_on_hold.pop(new_data_code, None)

                    response = post(f"http://127.0.0.1:8000/{endpoint}", json=new_data)
                    is_response_success = response.status_code == 200
                    status_success.append(is_response_success)
                    
                    if is_response_success:
                        if has_codes_by_endpoint:
                            codes_by_endpoint.add(new_data_code)
                    else:
                        error_messages.append(response.text)

                return all(status_success), error_messages

            
            logger.info("Parceo y carga de datos en proceso...")
            
            codes_alredy_stored = {
                "countries": set(),
                "provinces": set()
            }
            provinces_on_hold = {}
            for df_aux in (df_a, df_b):
                for index, row in df_aux.iterrows():
                    all_data = {
                        "countries": row_parse(row, "country"),
                        "provinces": row_parse(row, "province"),
                        "procedures": row_parse(row, "procedure"),
                    }

                    all_data["procedures"]["code_number"] = str(index)

                    is_all_successful, error_messages = post_all_data(all_data, codes_alredy_stored, provinces_on_hold)
                    if not is_all_successful:
                        logger.error(f"No se han podido enviar a la API los datos, errores: {error_messages}")


            if len(provinces_on_hold) != 0:
                is_all_successful, error_messages = send_hold_provinces(provinces_on_hold)
                if not is_all_successful:
                        logger.error(f"No se han podido enviar a la API los datos, errores: {error_messages}")

            logger.info("¡Peticiones POST Finalizadas!")

            

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