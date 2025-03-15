FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
  build-essential \
  python3-dev \
  python3-pip \
  python3-setuptools \
  python3-wheel \
  python3-cffi \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info \
  gettext \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1  

COPY . /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint-django.sh  /entrypoint-django.sh
RUN chmod +x /entrypoint-django.sh 
