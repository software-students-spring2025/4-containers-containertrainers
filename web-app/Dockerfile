# web-app/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /web-app

# System dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD . .

RUN mkdir -p /app/recordings
VOLUME ["/app/recordings"]

EXPOSE 3000

CMD ["python3", "src/app.py"]
