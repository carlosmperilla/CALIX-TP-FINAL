from typing import Union, List

from pydantic import BaseModel


class ProcedureBase(BaseModel):
    code_number: str
    type: str


class ProcedureCreate(ProcedureBase):
    province_code: str


class ProcedureNested(ProcedureBase):
    id: int


class Procedure(ProcedureNested, ProcedureCreate):

    class Config:
        orm_mode = True


class ProvinceBase(BaseModel):
    name: str
    code: str


class ProvinceCreate(ProvinceBase):
    country_code: str


class ProvinceNested(ProvinceBase):
    id: int


class Province(ProvinceNested, ProvinceCreate):
    procedures: List[ProcedureNested] = []

    class Config:
        orm_mode = True


class CountryBase(BaseModel):
    code: Union[str, None] = None
    name: str


class CountryCreate(CountryBase):
    pass


class Country(CountryBase):
    id: int
    provinces: List[ProvinceNested] = []

    class Config:
        orm_mode = True