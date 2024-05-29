FROM registry-bzh.alfred.cafe/breizh-ctf-2024/docker/web

ENV ADMIN_PASSWORD=a21cc45648b3eab9f5a0a05fccbc3fe6dc11f3eba252c9888efbfaab70228ea4

USER root

RUN apk add py3-pip chromium php-pdo chromium-chromedriver php-pdo_sqlite sqlite

COPY requirements.txt .

RUN pip3 install -r requirements.txt --break-system-packages

RUN mkdir /tmp/uploads/

RUN chown apache:apache /tmp/uploads/

COPY init.sql /tmp/init.sql
COPY web/ /challenge
COPY flag.txt /flag.txt

RUN sqlite3 /challenge/database.db < /tmp/init.sql 
RUN chmod 777 /challenge/database.db


RUN composer install
