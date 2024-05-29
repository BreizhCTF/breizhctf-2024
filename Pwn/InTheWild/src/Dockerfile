FROM ubuntu:22.04 AS builder

RUN apt update
RUN apt install -y gcc
RUN apt install -y make

WORKDIR /root
COPY main.c .
COPY Makefile .
RUN make

FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root

COPY --from=builder ./root/main /challenge/

COPY --chown=root:root flag.txt /flag.txt 
RUN mv /flag.txt /flag_$(md5sum /flag.txt | awk '{print $1}')

USER challenge

ENTRYPOINT '/challenge/main'