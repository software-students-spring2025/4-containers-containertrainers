# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /machine-learning-client

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ADD . .

EXPOSE 3000

ENV PYTHONDONTWRITEBYTECODE 1

CMD ["python", "client.py"]
