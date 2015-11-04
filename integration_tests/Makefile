.PHONY: test-setup test

test-setup:
	docker pull python:2.7
	docker pull p0bailey/docker-flask
	docker pull n3llyb0y/wait
	docker build -t xivo/xivo-amid ..
	docker build --no-cache -t xivo-amid-tests -f Dockerfile ..

test:
	nosetests
