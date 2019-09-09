.PHONY: test-setup test

test-setup: build-amid
	docker pull p0bailey/docker-flask
	docker pull wazopbx/wait

build-amid:
	docker build -t wazopbx/wazo-amid ..
	docker build --no-cache -t wazo-amid-tests -f Dockerfile ..

test:
	nosetests
