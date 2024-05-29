FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root

COPY challenge.py /challenge/challenge
COPY requirements.txt /challenge/

RUN pip3 install --break-system-packages  -r /challenge/requirements.txt

RUN chmod +x /challenge/challenge

USER challenge
