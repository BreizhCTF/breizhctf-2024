#!/bin/bash
rm -rf ./preprod/public/*
hugo -s ./preprod
docker compose up -d --force-recreate
