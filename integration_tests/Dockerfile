FROM wazopbx/xivo-amid

ENV PYTHONDONTWRITEBYTECODE='true'

ADD . /usr/src/xivo-amid
WORKDIR /usr/src/xivo-amid
RUN python setup.py develop
