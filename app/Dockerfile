FROM python:3.8

ADD requirements.txt requirements.txt

RUN pip install --upgrade --no-cache-dir -r requirements.txt

WORKDIR /code
ADD . /code

EXPOSE 5000

