FROM python:3.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN python -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY . /usr/src/wazo-amid
WORKDIR /usr/src/wazo-amid
RUN pip install -r requirements.txt
RUN python setup.py install

FROM python:3.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-amid /etc/wazo-amid
RUN true \
    && adduser --quiet --system --group --no-create-home wazo-amid \
    && install -o wazo-amid -g wazo-amid /dev/null /var/log/wazo-amid.log \
    && install -d -o wazo-amid -g wazo-amid /run/wazo-amid

EXPOSE 9491

ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-amid", "-d"]
