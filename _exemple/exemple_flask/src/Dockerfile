FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/python-flask

COPY --chown=root:root requirements.txt /challenge/

RUN pip3 install -r /challenge/requirements.txt

COPY --chown=root:root server.py /challenge/
