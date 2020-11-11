FROM alpine
RUN apk update && apk add --no-cache --upgrade  bash curl
COPY check_tor_continiously.sh check_tor_continiously.sh
RUN echo "[Proxy not started]" > out.txt
ENTRYPOINT [ "bash" ]
CMD [ "./check_tor_continiously.sh" , "2"]