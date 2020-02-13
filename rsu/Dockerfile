FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install paho-mqtt

CMD ["python3", "-O", "/usr/src/app/rsu.py"]
