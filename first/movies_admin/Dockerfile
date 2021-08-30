FROM python:3.9-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY ./movies_admin/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
