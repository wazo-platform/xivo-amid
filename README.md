wazo-amid
=========
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-amid)](https://jenkins.wazo.community/job/wazo-amid)

wazo-amid is a daemon for interacting Asterisk's AMI:

* forward AMI events to RabbitMQ
* expose HTTP JSON interface for AMI actions


Docker
------

The wazopbx/wazo-ami image can be built using the following command:

    docker build -t wazopbx/wazo-amid .


Testing
-------

wazo-amid contains unittests and integration tests


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```


Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
