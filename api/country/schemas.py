from typing import Union, List

from pydantic import BaseModel

from ..province.schemas import ProvinceNested


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