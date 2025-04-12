# web-app/Dockerfile
FROM python:3.9-slim-buster

RUN pip install pipenv

WORKDIR /app

# System dependencies
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ADD . /app

RUN mkdir -p /app/recordings
VOLUME ["/app/recordings"]

EXPOSE 3000

CMD ["python3", "src/app.py"]
