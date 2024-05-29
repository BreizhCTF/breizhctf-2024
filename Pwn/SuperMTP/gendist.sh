#!/usr/bin/env bash

set -xe

rm dist/supermtp.zip || true

mkdir -p dist/lib
cp src/lib/smtp.so dist/lib/
cp src/app.py dist

cd dist
zip -mr supermtp.zip lib app.py
zip -u supermtp.zip Dockerfile-player flag.txt 

cd -
