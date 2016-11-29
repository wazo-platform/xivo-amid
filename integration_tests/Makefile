.PHONY: test-setup test

test-setup: build-amid
	docker pull python:2.7
	docker pull p0bailey/docker-flask
	docker pull swaggerapi/swagger-validator
	docker pull n3llyb0y/wait

build-amid:
	docker build -t wazopbx/xivo-amid ..
	docker build --no-cache -t xivo-amid-tests -f Dockerfile ..

test:
	nosetests
