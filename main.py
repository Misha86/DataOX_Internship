import os
import requests
from bs4 import BeautifulSoup
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
    return sessionmaker(bind=eng)()


def get_html_content(page):
    url = f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273'
    with requests.get(url, stream=True) as r:
        html = r.content.decode('utf-8')
    return html


def get_data(html_info):
    price_ = html_info.find("div", attrs={"class": "price"}).text.strip().replace(",", "")
    currency = price_[0]
    try:
        price = float(price_[1:])
    except Exception:
        price = 0
    title = html_info.find("div", attrs={"class": "title"}).get_text(strip=" ")
    location = html_info.find("span", attrs={"class": ""}).get_text(strip=" ")
    date = html_info.find("span", attrs={"class": "date-posted"}).get_text(strip=" ")
    description = html_info.find("div", attrs={"class": "description"}).stripped_strings.__next__()
    image = html_info.find("div", attrs={"class": "image"}).find("img").get("data-src")
    if image is None:
        image = "https://ca.classistatic.com/static/V/11166/img/placeholder-large.png"
    bedrooms = html_info.find("span", attrs={"class": "bedrooms"}).text.replace("Beds:", "").strip()
    return image, title, date, location, description, bedrooms, price, currency


def run(engine):
    with get_session(engine) as session:
        current_page = 1
        while True:
            html_data = get_html_content(current_page)

            soup = BeautifulSoup(html_data, 'html.parser')

            info = soup.find_all("div", attrs={"class": "clearfix"})
            page = int(soup.find("span", attrs={"class": "selected"}).text)
            if current_page != page:
                break
            for i in info[1:]:
                image, title, date, location, description, bedrooms, price, currency = get_data(i)
                apartment = Apartment(image=image,
                                      title=title,
                                      date=date,
                                      city=location,
                                      description=description,
                                      bedrooms=bedrooms,
                                      price=price,
                                      currency=currency,
                                      page=page)
                session.add(apartment)
                session.commit()
            current_page += 1


if __name__ == "__main__":
    run(engine)
    os.system(f"pg_dump {settings['db_name']} > {settings['db_name']}_db.sql")
