FROM ubuntu:22.04 AS builder

RUN apt update
RUN apt install -y gcc-aarch64-linux-gnu
RUN apt install -y make

WORKDIR /root
COPY main.c .
COPY Makefile .
RUN make

FROM ubuntu:22.04
ENV TIMEZONE Europe/Paris

RUN apt-get update && apt-get install -y netcat socat python3-pip qemu-user && rm -rf /var/lib/apt/lists/*

COPY --chown=root:root flag.txt /flag.txt 
RUN mv /flag.txt /flag_$(md5sum /flag.txt | awk '{print $1}')

RUN useradd -u 666 --home=/challenge -U challenge
WORKDIR /challenge/

COPY --from=builder ./root/mte /challenge/
COPY ./lib /challenge/lib

USER challenge

ENV SOCAT_OPTIONS=",stderr,pty,cfmakeraw,echo=0"

#ENTRYPOINT ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'qemu-aarch64 -L /challenge/ /challenge/mte'${SOCAT_OPTIONS}"]
ENTRYPOINT ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'env -i qemu-aarch64 -L /challenge/ /challenge/mte'${SOCAT_OPTIONS}"]

HEALTHCHECK --interval=30s --timeout=3s \
    CMD nc -w 1 -v -z 127.0.0.1 1337 || exit 1
