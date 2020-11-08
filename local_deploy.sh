#!/bin/bash
docker-compose build
docker-compose down
docker-compose up -d
echo "Connecting to the log feed in 10 seconds"
sleep 10
docker-compose logs --follow