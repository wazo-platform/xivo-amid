test-setup:
	docker build -t wazoplatform/wazo-amid ..
	docker build --no-cache -t wazo-amid-tests -f Dockerfile ..

test:
	pytest

.PHONY: test-setup test
