.PHONY: *

_default: generate-iso

generate-iso: check-env
	cd src && LOG_LEVEL=DEBUG python3 main.py

check-env:
ifndef MULTIPASS_AUTH
	$(error env var MULTIPASS_AUTH is not set)
endif

flash-usb:
	hdiutil unmount /dev/disk4
	sudo dd if=src/preseeded-debian-12.1.0-amd64-netinst.iso of=/dev/disk4 bs=4M status=progress
