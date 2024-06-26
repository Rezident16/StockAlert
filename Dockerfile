FROM node:16-slim as build
RUN apt-get update && apt-get install -y python3 make g++ wget
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -R ta-lib ta-lib-0.4.0-src.tar.gz
COPY /react-app /react_app
WORKDIR /react_app
RUN npm install && CI=false && npm run build

FROM python:3.9
RUN apt-get update && apt-get install -y build-essential libpq-dev gfortran libopenblas-dev libxml2-dev libxslt-dev gcc python3-dev musl-dev wget
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -R ta-lib ta-lib-0.4.0-src.tar.gz
RUN apt-get install -y postgresql-client
ARG FLASK_APP
ARG FLASK_ENV
ARG DATABASE_URL
ARG SCHEMA
ARG REACT_APP_BASE_URL
ARG SECRET_KEY
WORKDIR /var/www
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install --upgrade setuptools
RUN pip install email_validator
RUN pip install psycopg2
COPY . .
COPY --from=build /react_app /var/www/react-app
RUN flask db upgrade
RUN flask seed all
CMD gunicorn app:app
