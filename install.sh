#!/bin/bash

set -u

DIR=$HOME/delta

mkdir $DIR
mkdir $DIR/data

cd ${DIR}

if [ ! -f "$DIR/.env" ]; then
  printf "DELTA_API_TOKEN=<Token>\nDELTA_API_URL=https://stage.delta.outsideopen.dev" > ${DIR}/.env
fi


curl https://raw.githubusercontent.com/outsideopen/delta-collectors/HEAD/docker-compose.yml -O
curl https://raw.githubusercontent.com/outsideopen/delta-collectors/HEAD/opencanary.conf -O

sudo docker-compose up -d
