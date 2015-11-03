FROM ubuntu:trusty
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get --yes update && apt-get --yes install build-essential g++ flex \
    bison gperf ruby perl libsqlite3-dev libfontconfig1-dev libicu-dev git \
    libfreetype6 libssl-dev libpng-dev libjpeg-dev libx11-dev libxext-dev \
    python python-dev python-pip
COPY . /spell-checker-server
RUN cd spell-checker-server && pip install -r requirements.txt
RUN git clone git://github.com/ariya/phantomjs.git && \
    cd phantomjs && \
    git checkout 2.0.0 && \
    ./build.sh  --confirm && \
    mv bin/phantomjs /spell-checker-server

EXPOSE 8080
CMD ["bin/bash"]
