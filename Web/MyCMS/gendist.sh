#!/usr/bin/env bash

set -xe

cp -r src/* dist

cd dist

echo "BZHCTF{fake_flag2}" > flag.txt
sqlite3 src/database/database.sqlite "UPDATE flag SET value='BZHCTF{fake_flag1}' WHERE id=1"
echo "[+] Flag1 is: "
sqlite3 src/database/database.sqlite "SELECT value FROM flag WHERE id=1"
echo "[+] Flag2 is: "
cat flag.txt
zip -rm mycms.zip 000-default.conf docker-compose.yml Dockerfile error_log_template.txt flag.txt getflag getflag.c php.ini run.sh src
