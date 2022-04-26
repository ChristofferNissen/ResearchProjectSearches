FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev libxslt-dev libxml2-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY consolidator.py consolidator.py
ENTRYPOINT [ "python3" ]
CMD [ "consolidator.py" ]