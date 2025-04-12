# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /machine-learning-client

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . .

EXPOSE 3000

ENV PYTHONDONTWRITEBYTECODE 1

CMD ["python", "client.py"]
