# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY ./src /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

EXPOSE 5000


CMD ["python", "app.py"]