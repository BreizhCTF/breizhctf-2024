FROM rust:alpine3.19 AS builder

WORKDIR /usr/src/app

COPY cveforfree/ .

RUN cargo build --release

FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp


USER root

COPY --from=builder /usr/src/app/target/release/cveforfree /challenge/challenge
COPY --from=builder /usr/src/app/flag.txt .

USER challenge

ENTRYPOINT ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/challenge/challenge${SOCAT_OPTIONS}"]

