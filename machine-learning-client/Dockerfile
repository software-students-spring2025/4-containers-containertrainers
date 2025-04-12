# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt

EXPOSE 3000
ENV PYTHONDONTWRITEBYTECODE 1
CMD ["python", "client.py"]
