FROM php:8.2-apache

RUN apt-get update && apt-get install -y libmagickwand-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/php/ext/imagick && \
    curl -fsSL https://github.com/Imagick/imagick/archive/06116aa24b76edaf6b1693198f79e6c295eda8a9.tar.gz | tar xvz -C "/usr/src/php/ext/imagick" --strip 1 && \
    docker-php-ext-install imagick dom && \
    a2enmod rewrite && \
    mkdir /tmp/sessions && \
    chmod 777 /tmp/sessions/

COPY ./src/ /var/www/html/
COPY ./apache2.conf /etc/apache2/
COPY ./php.ini /usr/local/etc/php/
COPY ./flag.txt /

RUN chmod 755 /var/www/html/ && chown root:root /var/www/html/
RUN chown www-data:www-data /var/www/html/*.php
RUN chown www-data:www-data /var/www/html/fetcher/*.php
RUN chown www-data:www-data /var/www/html/fetcher/helpers/*.php

USER www-data
