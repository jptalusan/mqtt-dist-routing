# FROM python:3.6
FROM linusmotu/rsu-base:1.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD requirements.txt .
RUN pip install -r requirements.txt
CMD [ "python3", "-u", "broker.py" ]