FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt install -y git
RUN git clone https://github.com/linusmotu/osmnx.git
RUN git clone https://github.com/linusmotu/networkx.git

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN apt-get update -y
RUN apt-get install -qq -y python3-rtree

WORKDIR /usr/src/app/osmnx
RUN pip3 install .

WORKDIR /usr/src/app/networkx
RUN pip3 install .

WORKDIR /usr/src/app
RUN pip3 install -r requirements.txt

CMD [ "python3", "-u", "rsu.py" ]
