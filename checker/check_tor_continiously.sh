#!/bin/bash
INTERVAL=${1:-10}
echo "Prints tor ip every $INTERVAL""s (override with arg)"
while true; do
	echo ""
	curl --socks5 0.0.0.0:9050 https://check.torproject.org/api/ip
	sleep $INTERVAL
done 
