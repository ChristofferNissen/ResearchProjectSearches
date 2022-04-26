#!/bin/bash
INTERVAL=${1:-10}
echo "Prints tor ip every $INTERVAL""s (override with arg)"
echo ""
while true; do
	curl -H "Accept: application/json" --proxy 0.0.0.0:16379 https://check.torproject.org/api/ip -o out.txt &>/dev/null
	cat out.txt
	echo ""
	sleep $INTERVAL
done 