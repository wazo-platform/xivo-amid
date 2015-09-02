xivo-amid
=========
[![Build Status](https://travis-ci.org/xivo-pbx/xivo-amid.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-amid)

xivo-amid is a daemon for interacting Asterisk's AMI:

* forward AMI events to RabbitMQ
* expose HTTP JSON interface for AMI actions


## Docker

The xivo/amid image can be built using the following command:

   % docker build -t xivo/xivo-amid .


## Testing

xivo-amid contains unittests and integration tests

### unittests

Dependencies to run the unittests are in the `requirements.txt` file.

    % pip install -r requirements.txt -r test-requirements.txt

To run the unittests

    % nosetests xivo_amid

### Integration tests

You need:

    - docker

A docker image named `amid-test` is required to execute the test suite.
To build this image execute:

    % cd integration_tests
    % pip install -r test-requirements.txt
    % make test-setup

`make test-setup` downloads a bunch of Docker images so it takes a long time,
but it only needs to be run when dependencies of xivo-amid change in any way
(new Python library, new server connection, etc.)

To execute the integration tests execute:

    % make test
