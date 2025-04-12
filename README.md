![lint-free](https://github.com/software-students-spring2025/4-containers-containertrainers/actions/workflows/lint.yml/badge.svg)

![Web App CI](https://github.com/software-students-spring2025/4-containers-containertrainers/actions/workflows/build_web.yml/badge.svg?branch=)

![ML Client CI](https://github.com/software-students-spring2025/4-containers-containertrainers/actions/workflows/build_ml.yml/badge.svg?branch=)

# The Speechily App

The speechily app is a lightweight portable dockerized webapp that uses machine learning technology to analyze a conversation or a single user.

It takes audio of speech, converts it to text, and semantically analyzes it.

It offers a solution for making insights into spoken conversation. It can be useful for both improving communication as well as personal development and reflection.

# Team Members:

[Ariya Mathrawala] (https://github.com/ariyamath29)
[Nikita Bhaskar] (https://github.com/nikitabhaskar)
[Jonathan Gao] (https://github.com/jg169)
[Gabriella Coddrington] (https://github.com/gabriella-codrington)

# Setup and Installation:

## Prerequisites

Install the following software on your machine:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://github.com/git-guides/install-git)
- [MongoDB](https://www.mongodb.com/docs/manual/installation/)

## Configuration

Clone the repository:

```shell
git clone https://github.com/software-students-spring2025/4-containers-containertrainers.git
```

### Run with Docker:

1. Build and Run

```shell
docker compose-up --build
```

2. Run Tests

```shell
docker exec -it . pytest
```

Access the web interface at http://127.0.0.1:3000

### Run without Docker:

1. Virtual Environment Setup

Using `pipenv`:\*\*

```shell
pip install pipenv
pipenv shell
```

Using `venv`:\*\*

```
python3 -m venv .venv
source .venv/bin/activate #On Mac
.venv\Scripts\activate.bat #On Windows
```

2. Install Dependencies

```shell
pip install -r requirements.txt
```

3. Create and populate your .env file in the project directory

```shell
MONGO_URI=[your connection string]
MONGO_DBNAME=speech2text
PORT=3000
```

4. Connect to database using mongosh

5. Run Application

```shell
cd src
python3 app.py
```

6. Run Tests

```shell
pytest tests/
```

Access the web interface at http://127.0.0.1:3000

# Task Board

[Task Board](https://github.com/orgs/software-students-spring2025/projects/207)
