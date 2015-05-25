.PHONY: test-image test-setup

test-setup:
	docker pull python:2.7
	docker pull quintana/amid
	docker pull rabbitmq

test-image:
	docker build --no-cache -t amid-test .
