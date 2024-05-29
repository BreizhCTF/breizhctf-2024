#!/bin/bash

docker build . -t got_you
docker run --name got_you got_you
docker cp got_you:/app/GotYou ../dist/
docker cp got_you:/app/glibc/build/libc.so ../dist/libc.so.6
docker cp got_you:/app/glibc/build/elf/ld.so ../dist/ld-linux-x86-64.so.2
docker rm got_you
docker rmi got_you

