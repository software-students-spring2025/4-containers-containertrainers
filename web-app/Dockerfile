# web-app/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /web-app

# System dependencies
COPY requirements.txt ./

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

ENV MONGO_DSN =mongodb+srv://nb3460:9paNoydyVz52hqhO@cluster0.zfwsq7e.mongodb.net/Speech2Text?retryWrites=true&w=majority&appName=Cluster0
ENV MONGO_DBNAME speech2text
ENV PORT 3000

CMD ["python3", "src/app.py"]
