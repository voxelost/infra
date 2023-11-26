import os
import time
import logging
from utils.multipass import Multipass


def build_iso(
    iso_filename: str,
    iso_url: str,
    target_config_name: str,
    target_iso_filename: str,
    multipass_auth: str,
    **_
):
    with Multipass(target_config_name, multipass_auth, disk="10GB") as multipass:
        # TODO: implement this logic:
        # https://github.com/raspberrypi/rpi-imager/blob/qml/src/OptionsPopup.qml#L589

        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd(
            "apt-get install --no-install-recommends -y build-essential devscripts debhelper cmake git libarchive-dev libcurl4-gnutls-dev liblzma-dev qtbase5-dev qtbase5-dev-tools qtdeclarative5-dev libqt5svg5-dev qttools5-dev libgnutls28-dev qml-module-qtquick2 qml-module-qtquick-controls2 qml-module-qtquick-layouts qml-module-qtquick-templates2 qml-module-qtquick-window2 qml-module-qtgraphicaleffects e2fsprogs unp"
        )
        # https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2023-10-10/2023-10-10-raspios-bookworm-arm64-lite.img.xz

        multipass.cmd("git clone --depth 1 https://github.com/raspberrypi/rpi-imager")
        multipass.cmd("debuild -uc -us", cwd="rpi-imager")
        multipass.cmd("dpkg -i ./rpi-imager*.deb")
        multipass.cmd("apt-get install -f")

        multipass.upload(
            "/Users/voxelost/workspace/devops/infra/homelab/provisioning/tools/os-img/debian/src/templates/first-run-raw.sh"
        )

        multipass.cmd("mkdir -p /dev/mock1")
        multipass.cmd("mkdir -p mock1")
        multipass.cmd("mount --bind /dev/mock1 mock1")

        multipass.cmd("rpi-imager --cli --first-run-script first-run-raw.sh")
