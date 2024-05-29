FROM debian:bookworm-slim

ENV TIMEZONE Europe/Paris

RUN apt-get update && apt-get install -y --no-install-recommends socat python3-pip && rm -rf /var/lib/apt/lists/*

RUN useradd -u 666 --home=/challenge -U challenge

WORKDIR /challenge/

USER challenge

COPY flag.txt .
COPY app.py .
COPY lib/smtp.so lib/smtp.so

ENV SOCAT_OPTIONS=",stderr,pty,cfmakeraw,echo=0"

USER challenge

ENTRYPOINT ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/challenge/app.py${SOCAT_OPTIONS}"]
