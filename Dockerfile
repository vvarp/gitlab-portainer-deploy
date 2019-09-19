FROM python:3.7-alpine

RUN apk add --no-cache ca-certificates

ADD . /app
WORKDIR /app
RUN python /app/setup.py install

CMD deploy
