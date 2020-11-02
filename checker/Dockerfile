FROM alpine
RUN apk update && apk add --no-cache --upgrade  bash curl
COPY check_tor_continiously.sh check_tor_continiously.sh
ENTRYPOINT [ "bash" ]
CMD [ "./check_tor_continiously.sh" , "3"]