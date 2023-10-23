import argparse
import os
import logging
from utils.multipass import Multipass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso-filename")
    parser.add_argument("--iso-url")
    parser.add_argument("--target-config-file")
    parser.add_argument("--target-iso-filename")
    parser.add_argument("--multipass-auth")
    # TODO: differentiate between debian and raspbian
    args = parser.parse_args()

    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

    _TARGET_OS = "debian"
    if _TARGET_OS == "debian":
        from builders.debian import build_iso
    elif _TARGET_OS == "raspbian":
        from builders.raspbian import build_iso

    build_iso(**args.__dict__)
