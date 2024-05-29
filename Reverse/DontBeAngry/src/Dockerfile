FROM ubuntu:22.04

RUN apt update

RUN apt install -y \
    cmake \
    python3

WORKDIR /app

COPY . .

RUN cmake -DCMAKE_BUILD_TYPE=Release .

RUN cmake --build .

RUN python3 gen_enc_file.py
