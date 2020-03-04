FROM python:3.6

COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY . /tmp/

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# ADD ./requirements.txt /usr/src/app/requirements.txt
# RUN pip3 install -r requirements.txt

CMD [ "python3", "-u", "broker.py" ]