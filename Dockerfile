FROM ubuntu:trusty
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get --yes update && apt-get --yes install build-essential g++ flex \
    bison gperf ruby perl libsqlite3-dev libfontconfig1-dev libicu-dev git \
    libfreetype6 libssl-dev libpng-dev libjpeg-dev libx11-dev libxext-dev \
    python python-dev python-pip
COPY . /spell-checker-server
RUN cd spell-checker-server && pip install -r requirements.txt

EXPOSE 8080
CMD ["/bin/bash"]
