#!/bin/bash
chattr +i /var/www/html/public/pdf/.htaccess
cd /var/www/html && php artisan key:generate
cd /root
apache2ctl -D FOREGROUND
