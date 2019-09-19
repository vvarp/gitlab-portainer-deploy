FROM python:3.7

RUN apt-get install ca-certificates

ADD . /app
WORKDIR /app
RUN python /app/setup.py install

CMD deploy
