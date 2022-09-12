FROM python:3.9.12-alpine

# Console output in real time and no *.pyc files
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copy project
WORKDIR /app
COPY . /app

# Install required packages
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev \
    linux-headers postgresql-dev postgresql-client
RUN apk add build-base
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt
