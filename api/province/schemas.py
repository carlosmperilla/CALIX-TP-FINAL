from typing import List

from pydantic import BaseModel

from ..procedure.schemas import ProcedureNested


class ProvinceBase(BaseModel):
    name: str
    code: str


class ProvinceCreate(ProvinceBase):
    country_code: str


class ProvinceNested(ProvinceBase):
    id: int

    class Config:
        orm_mode = True


class Province(ProvinceNested, ProvinceCreate):
    procedures: List[ProcedureNested] = []

    class Config:
        orm_mode = True


class ProvinciaProcedureCounter(BaseModel):
    province: str
    procedures_quantity: int