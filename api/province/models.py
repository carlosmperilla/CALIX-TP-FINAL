from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Province(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    country_code = Column(String, ForeignKey("countries.code", ondelete="CASCADE"))

    country = relationship("Country", back_populates="provinces")
    procedures = relationship("Procedure", back_populates="province")