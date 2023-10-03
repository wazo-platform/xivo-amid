FROM wazoplatform/wazo-amid

ENV PYTHONDONTWRITEBYTECODE='true'

ADD . /usr/src/wazo-amid
WORKDIR /usr/src/wazo-amid
RUN python3 -m pip install -e .
