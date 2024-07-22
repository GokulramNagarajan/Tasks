FROM alpine:3.14.1

ARG LFB_RT_SIMULATOR_URI=ws://localhost:5678
ARG POSTGRES_URI=postgresql://postgres:postgres@postgres/
ARG POSTGRES_HOSTNAME=postgres 
ARG POSTGRES_PORT=5432
ARG POSTGRES_USER=postgres
ARG POSTGRES_PASSWORD=postgres
ARG POSTGRES_DB=postgres

WORKDIR /app

RUN apk add --update build-base python3-dev py-pip
RUN apk add postgresql-client

COPY requirements.txt .
COPY src ./src

RUN pip install -r requirements.txt
