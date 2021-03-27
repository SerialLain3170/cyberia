FROM python:3.9

RUN apt-get update && apt-get install -y build-essential python-dev
RUN apt-get install -y nano
RUN apt-get install -y telnet

RUN pip3 install fastapi
RUN pip3 install requests
RUN pip3 install redis
RUN pip3 install uvicorn
RUN pip3 install jinja2
RUN pip3 install python-multipart
RUN pip3 install numpy
RUN pip3 install spotipy
RUN pip3 install pyyaml
RUN pip3 install mysql-connector-python
RUN pip3 install aiofiles

RUN mkdir src
COPY src/ /home/src/

WORKDIR /home/src
