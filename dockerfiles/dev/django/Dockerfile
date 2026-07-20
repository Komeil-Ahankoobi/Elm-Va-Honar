FROM python:3.13-slim

LABEL maintainer="ali.arezoomandi1723@gmail.com, komeilahankoobi@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt


COPY ./core .