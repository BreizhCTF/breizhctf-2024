FROM ubuntu:jammy

WORKDIR /opt/

ENV RUSTUP_HOME=/opt/rust
ENV CARGO_HOME=/opt/rust

RUN apt update && \
    apt install python3 python3-pip curl sudo netcat iproute2 -y && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | CARGO_HOME=/opt/rust RUSTUP_HOME=/opt/rust sh -s -- --no-modify-path -y && \
    chmod 711 /opt/rust/tmp

WORKDIR /root/

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN rm requirements.txt

WORKDIR /

ENTRYPOINT ["python3","/root/app.py"]