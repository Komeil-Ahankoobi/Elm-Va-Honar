FROM python:3.13-slim

LABEL maintainer="ali.arezoomandi1723@gmail.com, komeilahankoobi@gmail.com"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

# System packages needed to build psycopg / pillow wheels on slim images
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY ./core .
COPY dockerfiles/prod/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
