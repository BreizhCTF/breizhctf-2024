FROM ubuntu:22.04

RUN apt update

RUN apt install -y \
    cmake \
    make \
    git \
    gawk \
    bison \
    python3 \
    patchelf

WORKDIR /app

COPY . .

RUN git clone git://sourceware.org/git/glibc.git

WORKDIR glibc

RUN git checkout glibc-2.39

COPY glibc-2.39/elf/* ./elf/

COPY glibc-2.39/io/* ./io/

RUN mkdir build

WORKDIR build

RUN ../configure --disable-sanity-checks

RUN make -j7

WORKDIR /app

RUN cmake -DCMAKE_BUILD_TYPE=Release .

RUN cmake --build .
