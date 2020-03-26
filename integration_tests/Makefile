test-setup:
	docker build -t wazopbx/wazo-amid ..
	docker build --no-cache -t wazo-amid-tests -f Dockerfile ..

test:
	pytest

.PHONY: test-setup test
