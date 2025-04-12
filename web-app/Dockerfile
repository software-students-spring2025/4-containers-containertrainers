# web-app/Dockerfile
FROM python:3.9-slim-buster

RUN pip install pipenv

WORKDIR /app

# System dependencies
COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --system

ADD . /app

RUN mkdir -p /app/recordings
VOLUME ["/app/recordings"]

EXPOSE 3000

CMD ["python3", "src/app.py"]
