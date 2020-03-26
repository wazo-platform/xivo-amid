FROM python:3.7-buster
MAINTAINER Wazo Maintainers <dev@wazo.community>

ADD . /usr/src/wazo-amid
WORKDIR /usr/src/wazo-amid
RUN pip install -r requirements.txt \
    && python setup.py install \
    && adduser --quiet --system --group --no-create-home wazo-amid \
    && install -o wazo-amid -g wazo-amid /dev/null /var/log/wazo-amid.log \
    && install -d -o wazo-amid -g wazo-amid /run/wazo-amid \
    && cp -r etc/* /etc

EXPOSE 9491
CMD ["wazo-amid", "-fd"]
