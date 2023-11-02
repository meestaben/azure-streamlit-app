# app/Dockerfile

FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /app/
COPY requirements.txt /requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

RUN pip3 install -r /requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/entrypoint.sh"]