FROM ubuntu:20.04

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/code"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

RUN useradd -ms /bin/bash appuser

RUN mkdir /code && chown appuser:appuser /code

WORKDIR /code

COPY requirements.txt /code/

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python-dev \
    tzdata \
    python3-pip \
    gdal-bin \
    postgresql-client

RUN pip install -r requirements.txt
COPY . /code/
RUN chown -R appuser:appuser /code
#USER appuser

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.core.asgi:application"]
