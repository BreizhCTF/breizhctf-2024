FROM debian:bookworm-slim AS builder

RUN apt update
RUN apt install -y gcc
RUN apt install -y make

WORKDIR /root
COPY main.c .
COPY Makefile .
RUN make

FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root

COPY --from=builder ./root/usain_bolt /challenge/
COPY --chown=root:root flag.txt /flag.txt 

USER challenge

COPY ./run.sh /challenge/

ENTRYPOINT ["bash","/challenge/run.sh"]
