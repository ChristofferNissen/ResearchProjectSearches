#!/bin/bash
docker-compose build
docker-compose down
docker-compose up -d
echo "Connecting to the log feed in 3 seconds"
sleep 3
docker-compose logs --follow