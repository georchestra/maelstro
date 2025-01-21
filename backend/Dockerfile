FROM python:3.12-slim-bullseye

RUN pip install "fastapi[standard]" requests

RUN mkdir /app
COPY . /app

WORKDIR /app
