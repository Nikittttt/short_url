FROM python:3.9

ADD requirements.txt requirements.txt

RUN pip install --upgrade --no-cache-dir -r requirements.txt

WORKDIR /code
ADD . /code

