FROM python:3.8-alpine
LABEL maintainer="Galen Guyer <galen@galenguyer.com>"

RUN apk add git tzdata && \
    cp /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo "America/New_York" > /etc/timezone && \
    apk del tzdata

WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
ADD . /app

ENTRYPOINT ["gunicorn", "dr-ver:APP"]
