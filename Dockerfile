FROM python:2.7.9
MAINTAINER XiVO Team "dev@proformatique.com"

ADD . /usr/src/xivo-amid
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/src/xivo-amid
RUN pip install -r requirements.txt \
    && python setup.py install \
    && adduser --system --group --quiet --no-create-home --disabled-login xivo-amid \
    && install -o xivo-amid -g xivo-amid /dev/null /var/log/xivo-amid.log \
    && install -d -o xivo-amid -g xivo-amid /var/run/xivo-amid \
    && cp -r etc/* /etc

EXPOSE 9491
CMD ["xivo-amid", "-fd"]
