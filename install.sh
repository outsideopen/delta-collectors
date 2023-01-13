#!/bin/bash

set -u

DIR=$HOME/delta

mkdir -p $DIR
mkdir -p $DIR/data

cd ${DIR}

if [ ! -f "$DIR/.env" ]; then
  printf "DELTA_API_URL=https://app.digitalhydrant.com/api/upload\n" > ${DIR}/.env
  printf "HYDRANT_IP=($(hostname -i))\n" >> ${DIR}/.env
fi

curl https://raw.githubusercontent.com/outsideopen/delta-collectors/HEAD/docker-compose.yml -O
curl https://raw.githubusercontent.com/outsideopen/delta-collectors/HEAD/opencanary.conf -O

echo ""
echo "Follow these steps to start collecting"
echo "--------------------------------------"
echo "cd ${DIR}"
echo ""
echo "# Ensure that docker compose is installed"
echo "sudo apt install docker-compose"
echo ""
echo "# Get an API token"
echo "echo 'DELTA_API_TOKEN=[SUBSTITUE_TOKEN_VALUE_HERE]' >> ${DIR}/.env"
echo ""
echo "# Start the service"
echo "sudo docker-compose up -d"
