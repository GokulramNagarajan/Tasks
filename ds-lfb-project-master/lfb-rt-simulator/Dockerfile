FROM alpine:3.14.1

ARG CSV_FILE_LOCATION=data/LFB_Incident_data_from_January_2017.csv.gz
ARG PRODUCER_MAX_SLEEP_TIME_SECONDS=5
WORKDIR /app

RUN apk add --update py-pip

COPY requirements.txt .
COPY src ./src
COPY data ./data

RUN pip install -r requirements.txt
