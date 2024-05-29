FROM php:8.3-apache

RUN apt update && apt install uuid git unzip libpng-dev zlib1g-dev libzip-dev -y

RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer

RUN docker-php-ext-install zip

COPY ./php.ini /usr/local/etc/php/
COPY ./src/ /var/www/html/
COPY ./000-default.conf /etc/apache2/sites-available/
COPY ./flag.txt /root/flag.txt
COPY ./getflag  /
COPY ./.htaccess /var/www/html/public/pdf/
COPY ./run.sh /root/run.sh

WORKDIR /templates

COPY ./error_log_template.txt .
RUN touch errors.log error_log_template_beta.txt error_log_template_test.txt && \
    chmod 777 *	&& \
    chmod +x /root/run.sh

WORKDIR /var/www/html/

RUN composer install --ignore-platform-req ext-gd --no-dev

RUN a2enmod rewrite && \
    chmod -R ug+rwx ./storage/ && \
    chgrp -R www-data ./storage/ ./bootstrap/cache/ && \
    chown -R www-data:www-data ./database/ && \
    chown -R www-data:www-data ./public/pdf/ && \
    chown root:root /var/www/html/public/pdf/.htaccess && \
    chmod 777 /var/www/html/vendor/mpdf/mpdf/tmp/ && \
    chmod u+s /getflag

CMD ["/root/run.sh"]
