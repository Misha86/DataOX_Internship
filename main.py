from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import (database_exists, create_database)
from pg_settings import postgresql as settings

from models import (Apartment, Base)


def get_postgres_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    return create_engine(url, echo=True)


engine = get_postgres_engine(*settings.values())
Base.metadata.create_all(engine)


def get_session(eng):
    session = sessionmaker(bind=eng)
    return session()


with get_session(engine) as session, engine.connect() as connection:
    my = Apartment(image="upload/1.img",
                   title="Nice title",
                   date='2019/8/09/',
                   city="Rivne",
                   description="description",
                   beds=2,
                   price=1000.00,
                   currency="$")
    session.add(my)
    session.commit()
