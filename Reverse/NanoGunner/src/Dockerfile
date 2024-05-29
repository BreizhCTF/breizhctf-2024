FROM ubuntu:22.04

RUN apt update

RUN apt install -y \
    cmake \
    g++-multilib \
    libgtkmm-3.0-dev

WORKDIR /app

COPY . .

RUN cmake -DCMAKE_BUILD_TYPE=Release .

RUN cmake --build .

