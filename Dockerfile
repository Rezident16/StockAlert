# Stage 1: Build React App
FROM node:15-slim AS build
RUN apt-get update && apt-get install -y python make g++
COPY /react-app /react_app
WORKDIR /react_app
RUN npm install && CI=false npm run build

# Stage 2: Build Flask App
FROM python:3.9

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gfortran libopenblas-dev libxml2-dev libxslt-dev gcc python3-dev musl-dev postgresql-client && \
    apt-get clean

# Install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables (if needed)
ARG FLASK_APP
ARG FLASK_ENV
ARG DATABASE_URL
ARG SCHEMA
ARG REACT_APP_BASE_URL
ARG SECRET_KEY

WORKDIR /var/www

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install email_validator psycopg2

# Copy Flask app source code
COPY . .

# Copy React build from previous stage
COPY --from=build /react_app/build /var/www/react-app

# Run database migrations and seeds
RUN flask db upgrade && \
    flask seed all

# Set command to run the application
CMD gunicorn app:app
