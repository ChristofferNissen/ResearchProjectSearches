#!/bin/bash
docker-compose build
docker-compose push
vagrant provision
echo "Connecting to the log feed in 10 seconds"
sleep 10
vagrant ssh -c 'cd vagrant; docker-compose logs --follow'