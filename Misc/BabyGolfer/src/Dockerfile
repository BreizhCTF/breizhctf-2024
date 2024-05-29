FROM ubuntu:jammy

WORKDIR /opt/

RUN apt update && \
    apt install python3 python3-pip sudo -y

WORKDIR /root/

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN rm requirements.txt

WORKDIR /

RUN chmod 711 /tmp/

ENTRYPOINT ["python3","/root/app.py"]