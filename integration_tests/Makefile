test-setup:
	docker build -t wazopbx/wazo-amid ..
	docker build --no-cache -t wazo-amid-tests -f Dockerfile ..

test:
	nosetests

.PHONY: test-setup test
