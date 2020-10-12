# set alpine as the base image of the Dockerfile
FROM alpine:latest
EXPOSE 9050 9051

# update the package repository and install Tor
RUN apk update && apk add --no-cache --upgrade  tor bash

# Setup tor config
COPY docker/setup_tor_config.sh .
RUN ./setup_tor_config.sh

RUN chown -R tor /etc/tor

# Set `tor` as the default user during the container runtime
USER tor

# Set `tor` as the entrypoint for the image
ENTRYPOINT ["tor"]

# Set the default container command
# This can be overridden later when running a container
CMD ["-f", "/etc/tor/torrc"]