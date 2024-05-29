FROM debian:bookworm-slim

USER root
RUN apt-get update && apt install -y --no-install-recommends python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages qiling pwntools

WORKDIR /root/

COPY --chown=root:root ./rootfs/ ./rootfs
COPY --chown=root:root solve.py ./solve.py
COPY --chown=root:root ./emulator.py ./
COPY --chown=root:root ./map_syscall.py /usr/local/lib/python3.11/dist-packages/qiling/os/linux/map_syscall.py

USER root 

ENV PWNLIB_NOTERM="1"

#ENTRYPOINT ["python3","/root/solve.py"]
