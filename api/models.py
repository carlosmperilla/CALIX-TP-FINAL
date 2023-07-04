from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    code_number = Column(String, unique=True)
    type = Column(String)
    province_code = Column(String, ForeignKey("provinces.code", ondelete="CASCADE"))

    province = relationship("Province", back_populates="procedures")


class Province(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    country_code = Column(String, ForeignKey("countries.code", ondelete="CASCADE"))

    country = relationship("Country", back_populates="provinces")
    procedures = relationship("Procedure", back_populates="province")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)

    provinces = relationship("Province", back_populates="country")