FROM python:2.7.13-stretch
MAINTAINER Wazo Maintainers <dev@wazo.community>

ADD . /usr/src/xivo-amid
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/src/xivo-amid
RUN pip install -r requirements.txt \
    && python setup.py install \
    && adduser --quiet --system --group --no-create-home xivo-amid \
    && install -o xivo-amid -g xivo-amid /dev/null /var/log/xivo-amid.log \
    && install -d -o xivo-amid -g xivo-amid /var/run/xivo-amid \
    && cp -r etc/* /etc

EXPOSE 9491
CMD ["xivo-amid", "-fd"]
