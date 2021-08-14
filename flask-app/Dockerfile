FROM python:3.7.11-stretch

RUN apt-get update
RUN apt-get -y install libpoppler-cpp-dev

ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD [ "python", "app.py" ]