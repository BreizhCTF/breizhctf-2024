FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/tcp

USER root
RUN pip3 install --break-system-packages qiling pwntools
USER challenge

WORKDIR /challenge/

COPY --chown=root:root ./rootfs/ ./rootfs
COPY --chown=root:root server.py ./challenge
COPY --chown=root:root emulator.py ./
COPY --chown=root:root ./map_syscall.py /usr/local/lib/python3.11/dist-packages/qiling/os/linux/map_syscall.py

USER root 
RUN chmod +x challenge
USER challenge

ENV PWNLIB_NOTERM="1"
