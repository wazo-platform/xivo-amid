egg-info:
	cd .. && python setup.py egg_info

test-setup: egg-info amid amid-test

amid:
	docker build -t wazoplatform/wazo-amid ..

amid-test:
	docker build --no-cache -t wazo-amid-tests -f Dockerfile ..

test:
	pytest

.PHONY: test-setup test egg-info
