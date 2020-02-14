FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install paho-mqtt==1.5.0

CMD [ "python3", "-u", "rsu.py" ]
