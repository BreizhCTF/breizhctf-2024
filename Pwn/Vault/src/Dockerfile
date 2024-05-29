FROM debian:bookworm-slim AS builder

RUN apt update
RUN apt install -y gcc make

WORKDIR /root
COPY . ./
RUN make

FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root

COPY --chown=root:root flag.txt /flag.txt 
RUN mv /flag.txt /flag_$(md5sum /flag.txt | awk '{print $1}')
COPY --from=builder ./root/out/vault /challenge/

USER challenge

ENTRYPOINT '/challenge/vault'
