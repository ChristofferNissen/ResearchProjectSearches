FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev libxslt-dev libxml2-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY docker_scripts/geckodriver.sh geckodriver.sh 
RUN ./geckodriver.sh
COPY search.py search.py
COPY keyword/ keyword/
ENTRYPOINT [ "python3" ]
CMD [ "search.py" ]