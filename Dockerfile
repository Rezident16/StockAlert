FROM node:15-buster as build
RUN apt-get update --allow-releaseinfo-change && apt-get install -y python make g++
COPY /react-app /react_app
WORKDIR /react_app
RUN npm install && CI=false && npm run build
FROM python:3.9-slim-buster
RUN apt-get update --allow-releaseinfo-change && apt-get install -y build-essential postgresql libpq-dev gfortran libopenblas-dev libxml2-dev libxslt-dev
ARG FLASK_APP
ARG FLASK_ENV
ARG DATABASE_URL
ARG SCHEMA
ARG REACT_APP_BASE_URL
ARG SECRET_KEY
WORKDIR /var/www
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install email_validator
RUN pip install psycopg2
COPY . .
COPY --from=build /react_app /var/www/react-app
RUN flask db upgrade
RUN flask seed all
CMD gunicorn app:app
