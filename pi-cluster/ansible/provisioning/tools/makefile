.PHONY: *

_default: rpiboot


build_usbboot:
	$(info "Downloading and building usbboot")
	git clone --depth=1 https://github.com/raspberrypi/usbboot 2> /dev/null || (cd usbboot && git pull)
	cd usbboot; $(MAKE)

rpiboot: build_usbboot
	./usbboot/rpiboot

clean:
	cd usbboot && $(MAKE) clean
