FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root

COPY flag.txt /flag.txt
RUN mv /flag.txt /flag_$(md5sum /flag.txt | awk '{print $1}')

USER challenge

COPY ./main /challenge/challenge