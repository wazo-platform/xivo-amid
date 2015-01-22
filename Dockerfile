## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    apt-utils \
    python-pip \
    git \
    python-dev \
    libpq-dev \
    libyaml-dev 

# Install xivo-amid
WORKDIR /root
RUN git clone "git://github.com/xivo-pbx/xivo-amid"
WORKDIR xivo-amid
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-amid.log
RUN chown www-data: /var/log/xivo-amid.log
RUN mkdir -p /etc/xivo/xivo-amid
RUN mkdir /var/run/xivo-amid
RUN chown www-data: /var/run/xivo-amid
RUN cp -a etc/xivo/xivo-amid/xivo-amid.yml /etc/xivo/xivo-amid/

# Clean
RUN apt-get clean

CMD xivo-amid -d -f
