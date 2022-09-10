from sqlalchemy import Column
from sqlalchemy import (Integer, String, Date, Text, Float)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Apartment(Base):

    __tablename__ = "apartment"

    id = Column(Integer, primary_key=True)
    image = Column(String(300))
    title = Column(String(100))
    date = Column(Date)
    city = Column(String(100))
    description = Column(Text)
    bedrooms = Column(String(100))
    price = Column(Float(decimal_return_scale=2))
    currency = Column(String(1))
    page = Column(Integer)

    def __repr__(self):
        return self.title
