#!/usr/bin/env bash

sudo docker build -t usain_bolt_bzhctf2024 .
container_name=$(docker run --rm -d usain_bolt_bzhctf2024)
sudo docker cp $container_name:/challenge/usain_bolt ../dist/
sudo docker kill $container_name
