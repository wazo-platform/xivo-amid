FROM wazoplatform/wazo-amid

ENV PYTHONDONTWRITEBYTECODE='true'

ADD . /usr/src/wazo-amid
WORKDIR /usr/src/wazo-amid
RUN python setup.py develop
