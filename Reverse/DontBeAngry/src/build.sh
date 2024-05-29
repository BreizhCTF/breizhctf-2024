#!/bin/bash

docker build . -t dont_be_angry
docker run --name dont_be_angry dont_be_angry
docker cp dont_be_angry:/app/DontBeAngry ../dist/
docker cp dont_be_angry:/app/flag.enc ../dist/
docker rm dont_be_angry
docker rmi dont_be_angry

