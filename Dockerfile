## Image to build from sources

FROM python:2.7
MAINTAINER XiVO Team "dev@avencall.com"

# Install xivo-amid
ADD . /usr/src/xivo-amid
WORKDIR /usr/src/xivo-amid
RUN pip install -r requirements.txt

RUN python setup.py install

# Configure environment
ADD ./contribs/docker/certs /usr/share/xivo-certs
RUN install -o www-data -g www-data /dev/null /var/log/xivo-amid.log
RUN install -d -o www-data -g www-data /var/run/xivo-amid
RUN cp -r etc/* /etc

EXPOSE 9491

CMD xivo-amid -d -f
