# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN pip install pipenv

# Set the working directory in the container
WORKDIR /app

COPY ./machine-learning-client/requirements.txt ./machine-learning-client
RUN pip install -r ./machine-learning-client/requirements.txt

ADD . /app


EXPOSE 3000

ENV PYTHONDONTWRITEBYTECODE 1
CMD ["python", "client.py"]
