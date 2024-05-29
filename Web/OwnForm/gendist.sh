#!/usr/bin/env bash

set -xe

cp -r src/{keys,views,bot.js,departements.json,index.js,package.json,package-lock.json} dist

cd dist

zip -rm ownform.zip keys views bot.js departements.json index.js package.json package-lock.json
zip -u ownform.zip Dockerfile-player
