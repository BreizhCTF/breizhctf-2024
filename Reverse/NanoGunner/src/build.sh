#!/bin/bash

docker build . -t nano_gunner
docker run --name nano_gunner nano_gunner
docker cp nano_gunner:/app/NanoGunner ../dist/
docker rm nano_gunner
docker rmi nano_gunner

