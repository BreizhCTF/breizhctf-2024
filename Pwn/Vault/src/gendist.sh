#!/usr/bin/env bash

set -xe

docker build -t vault .
container_name=$(docker run --rm -d vault)
docker cp $container_name:/challenge/vault ../dist/
docker cp $container_name:/usr/lib/x86_64-linux-gnu/libc.so.6 ../dist/
docker cp $container_name:/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 ../dist/
docker kill $container_name

cd ../dist

zip vault.zip vagrant_provision.sh Vagrantfile libc.so.6 ld-linux-x86-64.so.2 vault

cd -
