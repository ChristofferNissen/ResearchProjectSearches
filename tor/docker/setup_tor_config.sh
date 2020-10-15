#!/bin/bash

# tor_password="scholarly_password"
# tor --hash-password $tor_password
# hashed_password=$(tor --hash-password $tor_password)
# echo "ControlPort 9051" | tee /etc/tor/torrc
# echo "HashedControlPassword $hashed_password" | tee -a /etc/tor/torrc

#service tor stop

#service tor start

# dirty hack to get torrc to work on Alpine. Generate file by running above commands on ubuntu
cat << EOF > /etc/tor/torrc
SocksPort 0.0.0.0:9050
ControlPort 0.0.0.0:9051
HashedControlPassword 16:77A8C7AD0E600338604F124CFA033B2F476531743F79B0126402A6D77D
EOF