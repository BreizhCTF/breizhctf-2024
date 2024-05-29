FROM ubuntu:22.04

RUN apt update

RUN apt install -y clang libssl-dev python3-dev  


WORKDIR /app

COPY . .

RUN clang mmm.c -I/usr/include/python3.10/ -lcrypto -I. -shared -fPIC -o Module.so 
