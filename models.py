from datetime import datetime, timedelta

from sqlalchemy import Column
from sqlalchemy import (Integer, String, Text, Float)
from sqlalchemy.orm import declarative_base, validates

Base = declarative_base()


class Apartment(Base):

    __tablename__ = "apartment"

    id = Column(Integer, primary_key=True)
    image = Column(String(300))
    title = Column(String(100))
    date = Column(String(50))
    city = Column(String(100))
    description = Column(Text)
    bedrooms = Column(String(100))
    price = Column(Float(decimal_return_scale=2))
    currency = Column(String(1), nullable=True)
    page = Column(Integer)

    @validates('date')
    def validate_date(self, key, date):
        formatted_date = date.replace("/", "-")
        time_delta = 0
        if formatted_date[0] == "<":
            data_delta = formatted_date.split()[1:3]
            arg = data_delta[-1]
            time_delta = timedelta(
                **dict(((arg if arg[-1] == 's' else arg + "s", int(data_delta[-2])),))
            )
        elif formatted_date == "Yesterday":
            time_delta = timedelta(days=1)
        formatted_date = (datetime.today().date() - time_delta).strftime('%d-%m-%Y') \
            if time_delta else formatted_date
        return formatted_date

    def __repr__(self):
        return self.title
