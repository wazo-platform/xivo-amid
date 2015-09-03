.PHONY: test-setup test

test-setup:
	docker pull python:2.7
	docker pull nickstenning/flask
	docker pull n3llyb0y/wait
	docker build -t xivo/xivo-amid ..
	docker build -t asterisk-ajam-mock -f Dockerfile-asterisk-ajam-mock ..
	docker build -t xivo-auth-mock -f Dockerfile-auth-mock ..
	docker build --no-cache -t xivo-amid-tests -f Dockerfile ..

test:
	nosetests
