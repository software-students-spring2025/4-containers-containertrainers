![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# The Speechily app 
 The speechily app is a lightweight portable dockerized webapp that uses machine learning technology to analyze a conversation or a single user. It takes audio of speech, converts it to text, and semantically analyzes it. It offers a solution for making insights into spoken conversation. It can be useful for both improving communication as well as personal development and reflection. 

## Team Members: 

[Ariya Mathrawala] (https://github.com/ariyamath29)
[Nikita Bhaskar] (https://github.com/nikitabhaskar) 
[Jonathan Gao] (https://github.com/jg169)
[Gabriella Coddrington] 

## Some prerequisites 
- Docker
- Docker Compose 
- Git
- Python 

## How to clone the repository and get set up 


### the recording feature

``` git clone https://github.com/software-students-spring2025/4-containers-containertrainers.git
```

then run
```
docker build -t speechily-audio-recorder .
docker volume create recordings
docker run -p 5000:5000 -v recordings:/app/recordings speechily-audio-recorder
```
open your browser to the localhost:5000 http address you see. 

to access the recordings open speechily-recordings in the volumes section of docker desktop 

