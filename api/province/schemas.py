from typing import Union, List

from pydantic import BaseModel

from ..procedure.schemas import ProcedureNested


class ProvinceBase(BaseModel):
    name: str
    code: str


class ProvinceCreate(ProvinceBase):
    country_code: Union[str, None]


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