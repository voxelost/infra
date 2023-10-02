.PHONY: *

_default: generate-iso

generate-iso: check-env
	cd src && LOG_LEVEL=DEBUG python3 main.py

check-env:
ifndef MULTIPASS_AUTH
	$(error env var MULTIPASS_AUTH is not set)
endif
