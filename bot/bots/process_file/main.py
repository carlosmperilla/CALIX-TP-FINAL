from os.path import join
from typing import List

from pandas import read_csv, Series, DataFrame

from .constants import (
                        FILES_PATH,
                        FILE_TYPE
                        )

from utils.logger import logger

from ..send_data import SendData

class ProcessFile:

    FILES_PATH = FILES_PATH
    FILE_TYPE = FILE_TYPE
    KEY_MATCHING = {
        "procedure": {
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
    DTYPE = {
        "automotor_tipo_codigo": object, 
        "titular_domicilio_provincia_id": str
        }
    READ_FILE_METHODS = {
        "CSV": read_csv
    }

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.file_path = join(self.FILES_PATH, file_name)
        self.package_a_conditions = [
            "automotor_anio_modelo > 2015",
            "registro_seccional_provincia == 'Formosa'",
            "automotor_origen == 'Nacional'"
        ]
        self.package_b_conditions = [
            "registro_seccional_codigo == 1216",
            "automotor_origen == 'Importado'"
        ]
        self.df = self.read_file()
        self.send_data = SendData()


    def row_parse(self, row: Series, table_name: str) -> dict:
        """
            - Parsea la Serie del Dataframe, filtrando solo las columnas necesarias.
            - Las renombra al estandar de manejado por la API,
            - La convierte a un diccionario y lo retorna.
        """
        return row[self.KEY_MATCHING[table_name].keys()].rename(self.KEY_MATCHING[table_name]).to_dict()


    def arming_package(self, conditions: List[str]) -> DataFrame:
        """
            Une condiciones y regresa el dataframe filtrado.
        """
        return self.df.query(" and ".join(conditions))


    def read_file(self) -> DataFrame:
        """
            Lee el archivo tomando en cuenta el metodo,
            en base al tipo de archivo configurado.
            Le asigna dtypes custom, por cuestiones de compatibilidad o casteo.
        """
        return self.READ_FILE_METHODS.get(self.FILE_TYPE)(self.file_path, dtype=self.DTYPE)


    def parse_and_post_data(self, df_aux: DataFrame):
        """
            Parsea la fila, para poder enviarla a la API,
            envía los datos parseados.
            Si no fue exitoso en el envío, notifica los errores de la API
        """
        for index, row in df_aux.iterrows():
            all_data = {
                "countries": self.row_parse(row, "country"),
                "provinces": self.row_parse(row, "province"),
                "procedures": self.row_parse(row, "procedure"),
            }

            all_data["procedures"]["code_number"] = str(index)

            is_all_successful, error_messages = self.send_data.post_all_data(all_data)
            if not is_all_successful:
                logger.error(f"No se han podido enviar a la API los datos, errores: {error_messages}")


    def run(self):
        """
            Arma los dos conjuntos o paquetes en base a condiciones.
            Parsea y envia a la api los datos,
            Envía las provincias holdeadas (aquellas que poseían country_code: None),
            Si los conjuntos no poseen información suficiente para asignarlo (a country_code).
        """
        df_a = self.arming_package(self.package_a_conditions)
        df_b = self.arming_package(self.package_b_conditions)
        
        logger.info("Parceo y carga de datos en proceso...")
        
        for df_aux in (df_a, df_b):
            self.parse_and_post_data(df_aux)

        if self.send_data.has_provinces_on_hold():
            is_all_successful, error_messages = self.send_data.send_hold_provinces()
            if not is_all_successful:
                    logger.error(f"No se han podido enviar a la API los datos, errores: {error_messages}")

        logger.info("¡Peticiones POST Finalizadas!")