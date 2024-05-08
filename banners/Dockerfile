FROM python:3.11.4-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /app/entrypoint.sh

COPY . /app/
ENTRYPOINT [ "/app/entrypoint.sh" ]

