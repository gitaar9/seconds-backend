FROM python:3
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

