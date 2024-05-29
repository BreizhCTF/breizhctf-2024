#!/bin/bash

docker build . -t cant_follow -f Dockerfile-build
docker run --name cant_follow cant_follow
docker cp cant_follow:/app/CantFollow ../dist/
docker rm cant_follow
docker rmi cant_follow
