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
    ssh \
    libpq-dev \
    python-dev \
    libyaml-dev \
    nginx \
    vim \
    net-tools

# Install xivo-amid
WORKDIR /root
RUN git clone "git://github.com/xivo-pbx/xivo-amid"
WORKDIR xivo-amid
RUN git checkout -t origin/poc_alpha42
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-amid.log
RUN chown www-data: /var/log/xivo-amid.log
RUN cp debian/xivo-amid.init /etc/init.d/xivo-amid
RUN mkdir -p /etc/xivo/xivo-amid
RUN mkdir /var/run/xivo-amid
RUN chown www-data: /var/run/xivo-amid
RUN cp -a etc/xivo/xivo-amid/xivo-amid.yml /etc/xivo/xivo-amid/

# Configure nginx
RUN cp etc/nginx/sites-available/xivo-amid /etc/nginx/sites-available/xivo-amid
RUN ln -s /etc/nginx/sites-available/xivo-amid /etc/nginx/sites-enabled/xivo-amid

# Add script to run services
ADD xivo-amid-service /root/xivo-amid-service
RUN chmod +x /root/xivo-amid-service

# Set password
RUN echo "root:xivo" | chpasswd

# Clean
RUN apt-get clean

EXPOSE 50061

CMD /root/xivo-amid-service
