from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from . import models
from . import schemas
from ..utils import get_db


router = APIRouter(prefix="/procedures")


@router.post("/", response_model=schemas.Procedure, tags=["Procedure"])
def create_procedure(procedure: schemas.ProcedureCreate, db: Session = Depends(get_db)):
    db_procedure = models.Procedure(code_number=procedure.code_number, type=procedure.type, province_code=procedure.province_code)
    try:
        db.add(db_procedure)
        db.commit()
        db.refresh(db_procedure)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El procedimiento ya fue ingresado previamente")
    return db_procedure


@router.get("/{code_number}", response_model=schemas.Procedure, tags=["Procedure"])
def get_procedure(code_number: str, db: Session = Depends(get_db)):
    procedure = db.query(models.Procedure).filter(models.Procedure.code_number == code_number).first()
    if procedure is None:
        raise HTTPException(status_code=404, detail="Procedimiento no encontrado")
    return procedure


@router.get("/", response_model=List[schemas.Procedure], tags=["Procedure"])
def get_procedures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    procedures = db.query(models.Procedure).offset(skip).limit(limit).all()
    return procedures
