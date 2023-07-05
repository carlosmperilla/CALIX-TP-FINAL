from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from . import models
from . import schemas
from ..utils import get_db


router = APIRouter(prefix="/countries")


@router.post("/", response_model=schemas.Country, tags=["Country"])
def create_country(country: schemas.CountryCreate, db: Session = Depends(get_db)):
    db_country = models.Country(code=country.code, name=country.name)
    try:
        db.add(db_country)
        db.commit()
        db.refresh(db_country)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El país ya fue ingresado previamente")
    return db_country


@router.get("/{code}", response_model=schemas.Country, tags=["Country"])
def get_country(code: str, db: Session = Depends(get_db)):
    country = db.query(models.Country).filter(models.Country.code == code).first()
    if country is None:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return country


@router.get("/", response_model=List[schemas.Country], tags=["Country"])
def get_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = db.query(models.Country).offset(skip).limit(limit).all()
    return countries
