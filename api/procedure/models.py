from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    code_number = Column(String, unique=True)
    type = Column(String)
    province_code = Column(String, ForeignKey("provinces.code", ondelete="CASCADE"))

    province = relationship("Province", back_populates="procedures")