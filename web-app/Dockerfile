# web-app/Dockerfile

FROM python:3.9-slim-buster

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest
RUN pip install --no-cache-dir pytest pytest-cov

COPY . .

RUN mkdir -p /app/recordings
VOLUME ["/app/recordings"]

EXPOSE 3000

CMD ["python3", "src/app.py"]
