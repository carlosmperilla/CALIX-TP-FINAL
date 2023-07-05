from pydantic import BaseModel


class ProcedureBase(BaseModel):
    code_number: str
    type: str


class ProcedureCreate(ProcedureBase):
    province_code: str


class ProcedureNested(ProcedureBase):
    id: int

    class Config:
        orm_mode = True


class Procedure(ProcedureNested, ProcedureCreate):

    class Config:
        orm_mode = True