FROM python:3.7-alpine

ADD . /app
WORKDIR /app
RUN python /app/setup.py install

CMD deploy
