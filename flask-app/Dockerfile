FROM python:3.7.11-stretch

RUN apt-get update
RUN apt-get -y install libpoppler-cpp-dev

ADD . /app
WORKDIR /app

# This one works faster because of caching (for non-initial builds)
RUN pip install flask==2.0.1 pdftotext==2.1.6 regex==2021.8.3 pytest==6.2.4
# RUN pip3 install -r requirements.txt

CMD [ "python", "app.py" ]