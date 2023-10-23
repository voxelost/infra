import os
import time
import logging
from utils.multipass import Multipass


def build_iso(
    iso_filename: str,
    iso_url: str,
    target_config_file: str,
    target_iso_filename: str,
    multipass_auth: str,
):
    with Multipass(target_config_file, multipass_auth, disk="20G") as multipass:
        # TODO: implement this logic:
        # https://github.com/raspberrypi/rpi-imager/blob/qml/src/OptionsPopup.qml#L589

        logging.debug(multipass)
