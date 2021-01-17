#!/bin/bash
ARG1=${1:-scraperserver1}
docker-compose build
docker-compose push
vagrant provision $ARG1
echo "Connecting to the log feed in 10 seconds"
sleep 10
vagrant ssh $ARG1 -c 'cd /vagrant; docker-compose logs --tail="1000" --follow'