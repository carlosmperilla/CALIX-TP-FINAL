from typing import Tuple, List
from threading import Thread
from queue import Queue

from requests import post

from pandas import isna

from utils.logger import logger


class SendData:

    URL_BASE = "http://127.0.0.1:8000"

    def __init__(self):
        self.provinces_on_hold = {}
        self.codes_alredy_stored = {
            "countries": set(),
            "provinces": set()
        }
        self.status_success = []
        self.error_messages = []
        self.threads = []
        self.data_queue = Queue()

    def skip_endpoint(self, endpoint: str, new_data_code) -> Tuple[bool, List[str], bool]:
        """
            Se salta la petición al endpoint si Country o Province, ya fue enviado exitosamente.
        """
        codes_by_endpoint = self.codes_alredy_stored.get(endpoint)
        has_codes_by_endpoint = codes_by_endpoint is not None
        is_skipped = False
        if has_codes_by_endpoint:
            is_skipped = new_data_code in codes_by_endpoint
        return is_skipped, codes_by_endpoint, has_codes_by_endpoint
    
    def handle_province_holding(self, endpoint: str, new_data: dict) -> bool:
        """
            Mientras contry_code sea nulo se almacena su provincia, y se salta la petición.
            Una vez encontrado un valor no nulo para country_code se envía la petición.
        """
        new_data_code = new_data.get("code")
        is_skipped = False

        if endpoint == "provinces":
            if new_data.get("country_code") is None:
                self.provinces_on_hold[new_data_code] = new_data
                is_skipped = True
            else:
                unholding = self.provinces_on_hold.pop(new_data_code, None)
                if unholding is not None:
                    logger.info(f"Desholdeando {unholding} - se enviara {new_data} - motivo: Se encontro un country_code distinto de None")

        return is_skipped
       
    def post_data(self, endpoint: str, data: dict) -> Tuple[bool, str]:
        """
            Realiza una petición post a la API, parseando la información a JSON,
            Regresa si fue exitosa la petición y el mensaje de respuesta.
        """
        response = post(f"{self.URL_BASE}/{endpoint}", json=data)
        return response.status_code == 200, response.text
    
    def post_data_thread(self, endpoint: str, new_data: dict):
        """
            Realiza la petición y encola la información obtenida.
        """
        info = (endpoint, new_data, *self.post_data(endpoint, new_data))
        self.data_queue.put(info)

    def post_all_data(self, all_data: dict) -> Tuple[bool, List[str]]:
        """
            Envía toda la data que se puede extraer de una fila.
        """
        self.status_success = []
        self.error_messages = []
        self.threads = []
        nan_to_none = lambda value: None if isna(value) else value

        for endpoint, data in all_data.items():
            new_data = {key: nan_to_none(value) for key, value in data.items()}
            new_data_code = new_data.get("code")

            is_skipped, *_ = self.skip_endpoint(endpoint, new_data_code)
            if is_skipped:
                logger.info(f"Salteando {endpoint} con {new_data} - motivo: Ya registrada")
                continue
                
            is_skipped = self.handle_province_holding(endpoint, new_data)
            if is_skipped:
                logger.info(f"Salteando (temporalmente) {endpoint} con {new_data} - motivo: Holdeo de Provincia hasta encontrar country_code distinto de None")
                continue

            thread = Thread(target=self.post_data_thread, args=(endpoint, new_data))
            self.threads.append(thread)
            thread.start()
            
        for thread in self.threads:
            thread.join()

        self.cache_codes()

        return all(self.status_success), self.error_messages

    def cache_codes(self):
        """
            Guarda en cache los codigos y los estados de exito.
        """
        while not self.data_queue.empty():
            endpoint, new_data, is_response_success, response_text = self.data_queue.get()
            new_data_code = new_data.get("code")
            _, codes_by_endpoint, has_codes_by_endpoint = self.skip_endpoint(endpoint, new_data_code)
            self.status_success.append(is_response_success)
            if is_response_success:
                if has_codes_by_endpoint:
                    codes_by_endpoint.add(new_data_code)
            else:
                self.error_messages.append(response_text)

    def has_provinces_on_hold(self) -> bool:
        """
            Si hay provincias holdeadas.
        """
        return len(self.provinces_on_hold) != 0
    

    def send_hold_provinces(self) -> Tuple[bool, List[str]]:
        """
            Envía las provincias holdeadas, realizando una petición a la API.
        """
        status_success = []
        error_messages = []
        for province_data in self.provinces_on_hold.values():
            response = post(f"{self.URL_BASE}/provinces", json=province_data)
            is_response_success = response.status_code == 200
            status_success.append(is_response_success)

            if not is_response_success:
                error_messages.append(response.text)

        logger.warning("Algunas provincias tienen country_code nulo, enviando...")
        logger.info(f"Enviadas provincias en hold: {status_success} - {error_messages}")

        return all(status_success), error_messages