FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root
RUN apt-get update && apt-get install -y --no-install-recommends binutils-aarch64-linux-gnu binutils-arm-linux-gnueabi && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages unicorn pwntools
USER challenge

WORKDIR /challenge/

COPY --chown=root:root server.py ./challenge
COPY --chown=root:root arch_generators.py ./

USER root 
RUN chmod +x challenge
USER challenge

ENV PWNLIB_NOTERM="1"

