#!/usr/bin/env bash

sudo docker build -t mte_bzhctf2024 .
container_name=$(docker run --rm -d mte_bzhctf2024)
sudo docker cp $container_name:/challenge/mte ../dist/
cp -r ./lib ../dist/
sudo docker kill $container_name
cd ../dist/
zip -r mte.zip docker-compose.yml Dockerfile-player flag.txt
zip -urm mte.zip mte lib
cd -
