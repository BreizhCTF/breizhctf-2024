#!/usr/bin/env bash

set -xe

cp -r src/{public,views,bot.js,cards.json,index.js,package.json} dist

cd dist

zip -mr clickodrome.zip public views bot.js cards.json index.js package.json
zip -u clickodrome.zip Dockerfile-player

cd -
