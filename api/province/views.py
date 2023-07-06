from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from . import models
from ..procedure import models as procedure_models
from . import schemas
from ..utils import get_db


router = APIRouter(prefix="/provinces")


@router.post("/", response_model=schemas.Province, tags=["Province"])
def create_province(province: schemas.ProvinceCreate, db: Session = Depends(get_db)):
    db_province = models.Province(name=province.name, code=province.code, country_code=province.country_code)
    try:
        db.add(db_province)
        db.commit()
        db.refresh(db_province)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="La provincia ya fue ingresada previamente")
    return db_province


@router.get("/{code}", response_model=schemas.Province, tags=["Province"])
def get_province(code: str, db: Session = Depends(get_db)):
    province = db.query(models.Province).filter(models.Province.code == code).first()
    if province is None:
        raise HTTPException(status_code=404, detail="Provincia no encontrada")
    return province


@router.get("/", response_model=List[schemas.Province], tags=["Province"])
def get_provinces(skip: int = 0, limit: int = -1, db: Session = Depends(get_db)):
    provinces = db.query(models.Province).offset(skip).limit(limit).all()
    return provinces


@router.get("/{code}/procedures_quantity", response_model=schemas.ProvinciaProcedureCounter, tags=["Province"])
def get_procedures_quantity_by_province(code: str, db: Session = Depends(get_db)):
    province = get_province(code, db)
    # Se hace la operación de cuenta desde la base de datos en lugar de python.
    # Lo cual para este caso es más eficiente.
    procedures_quantity = db.query(procedure_models.Procedure).filter(procedure_models.Procedure.province_code == code).count()
    provincia_procedure_counter = {"province": province.name, "procedures_quantity": procedures_quantity}
    return provincia_procedure_counter


@router.get("/{code}/procedures", response_model=List[schemas.ProcedureNested], tags=["Province"])
def get_procedures_by_province(code: str, db: Session = Depends(get_db)):
    province = get_province(code, db)
    procedures = province.procedures
    return procedures