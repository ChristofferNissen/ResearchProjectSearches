FROM python

COPY requirements.txt . 
RUN pip install -r requirements.txt

RUN apt-get update -y
RUN apt-get install -y tor
COPY tor/setup_tor.sh . 

RUN useradd -rm -d /home/python -s /bin/bash -g root -G sudo -u 1001 python
RUN apt-get install -y sudo
RUN echo "python  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER python
RUN ./setup_tor.sh

WORKDIR /home/python

COPY search.py . 

ENTRYPOINT [ "python"]
CMD [ "search.py"]
