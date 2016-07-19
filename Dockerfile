FROM ubuntu:xenial
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get --yes update && \
    apt-get --yes install fontconfig python python-dev python-pip
COPY ./server /spell-checker-server
WORKDIR /spell-checker-server
RUN pip install -r requirements.txt

EXPOSE 80
CMD ["/spell-checker-server/start-server.sh"]
