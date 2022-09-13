import os
import time
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import (database_exists, create_database)

from models import (Apartment, Base)
from decouple import config


def get_postgres_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    return create_engine(url, echo=True)


engine = get_postgres_engine(user=config("POSTGRES_USER"),
                             passwd=config("POSTGRES_PASSWORD"),
                             host=config("POSTGRES_HOST"),
                             port=config("POSTGRES_PORT"),
                             db=config("POSTGRES_DB"))
Base.metadata.create_all(engine)


def get_session(eng):
    return sessionmaker(bind=eng)()


def get_html_content(page):
    url = f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273'
    try:
        with requests.get(url, stream=True) as r:
            html = r.content.decode('utf-8')
    except requests.exceptions.ChunkedEncodingError:
        time.sleep(10)
        html = get_html_content(page)
    return html


def check_price(pr):
    try:
        price = float(pr[1:])
        currency = pr[0]
    except Exception:
        price = 0
        currency = ""
    return price, currency


def check_image(image):
    if image is None:
        image = "https://ca.classistatic.com/static/V/11166/img/placeholder-large.png"
    return image


def get_data(html_info):
    price_ = html_info.find("div", attrs={"class": "price"}).text.strip().replace(",", "")
    price, currency = check_price(price_)
    title = html_info.find("div", attrs={"class": "title"}).get_text(strip=" ")
    location = html_info.find("span", attrs={"class": ""}).get_text(strip=" ")
    date = html_info.find("span", attrs={"class": "date-posted"}).get_text(strip=" ")
    description = html_info.find("div", attrs={"class": "description"}).stripped_strings.__next__()
    image = html_info.find("div", attrs={"class": "image"}).find("img").get("data-src")
    bedrooms = html_info.find("span", attrs={"class": "bedrooms"}).text.replace("Beds:", "").strip()
    return check_image(image), title, date, location, description, bedrooms, price, currency


def save_data(engine):
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
                session.add(Apartment(image=image,
                                      title=title,
                                      date=date,
                                      city=location,
                                      description=description,
                                      bedrooms=bedrooms,
                                      price=price,
                                      currency=currency,
                                      page=page))
            session.commit()
            current_page += 1


if __name__ == "__main__":
    save_data(engine)
    os.system(f"PGPASSWORD='{config('POSTGRES_PASSWORD')}' pg_dump -h {config('POSTGRES_HOST')} "
              f"-U {config('POSTGRES_USER')} -d {config('POSTGRES_DB')} > {config('POSTGRES_DB')}_db.sql")
