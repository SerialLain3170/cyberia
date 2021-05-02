#!/bin/bash

docker build -t fastapi -f Dockerfiles/FastAPI/Dockerfile .
docker build -t nginx -f Dockerfiles/Nginx/Dockerfile .
docker build -t mysql -f Dockerfiles/MySQL/Dockerfile .