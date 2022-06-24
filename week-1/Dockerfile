FROM python:3.9.1

RUN apt-get update -y && apt-get upgrade -y

WORKDIR /data-ingestion

COPY ./requirements.txt /data-ingestion/requirements.txt

RUN pip install -r requirements.txt

COPY ./pipeline.py /data-ingestion/pipeline.py
