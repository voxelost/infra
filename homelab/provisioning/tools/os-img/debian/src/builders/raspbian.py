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
    iso_filename = "2023-10-10-raspios-bookworm-arm64-lite.img"
    target_config_file = "configs/cm4.yml"
    target_iso_filename = "preseeded-2023-10-10-raspios-bookworm-arm64-lite.img"

    with Multipass(target_config_file, multipass_auth, disk="20G") as multipass:
        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd(
            "apt-get -y install coreutils quilt parted qemu-user-static debootstrap zerofree zip \
                        dosfstools libarchive-tools libcap2-bin grep rsync xz-utils file git curl bc \
                        qemu-utils kpartx gpg pigz"
        )



        multipass.cmd(
            "git clone -b bullseye-arm64 --depth 1 https://github.com/RPi-Distro/pi-gen",
            become=False,
        )
        multipass.cmd(
            "git reset --hard e484aa85818428c3af08de0ba1db5329dfc84143",
            cwd="pi-gen",
            become=False,
        )
        multipass.cmd(
            "git config --global --add safe.directory /home/ubuntu/workspace/pi-gen"
        )

        config = {
            "IMG_NAME": "raspbian",
            "DEPLOY_COMPRESSION": "none",
            "TARGET_HOSTNAME": "host",
            "KEYBOARD_KEYMAP": "us",
            "KEYBOARD_LAYOUT": "us",
            "TIMEZONE_DEFAULT": "Europe/Warsaw",
            # "FIRST_USER_NAME": "debian",
            "ENABLE_SSH": 1,
            "PUBKEY_ONLY_SSH": 1,
            "PUBKEY_SSH_FIRST_USER": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAD9QD3Ktvnq5P9oa4XxZ/h1tSAQnGdZkjAxCU0jlZ1UsWp9hf0/vRLlvHa6B6xaaaZZfaIuUkh3Y+y6obRbul+SZ1ru8ixj+KJkl0b0ZL20PJ0lbN3n8IiE1x53xCsXkjt0F7GHVmzUMuyguff0bnCd2Nf6O0u6ja0766NwJ5G565lBkZT7Q4u38+XZSFH4r9F9emWZxEF9EfteF8LqyLlCDAcrPDbe6iqhXqjUlTD6uNORMKh1i1U49yB6khNcy2rwJYuIFtd0KSqShhHBkWGdrsUnjN7KEEuc0ORvfryJDaEcIoqodXcYbHH2W0gE4DHl71n4l2/XKg5z1NzUWcxcJWSnmfwTkynVFqpdAm0hz+54andsya9exHbgWkqsoaZx/ecZNUySoIgnQGXp+yGUg6q0DwVDA4EdWhlmwSpJ+EU6tozzaxsRK7mZZTpC4sz/wnJNb5itjAS2vd3wxslPRliIyQFvNrNc5bGY9G4ECA6+CbVh8KexSNZD08udypiVO875TZM0WUbN+TmTtjfMAcdfYji0ZNRMv02nnMkll754KKe9BplzAjNYKy7ol3rb9/shA/aoihEi7pLhUEl6jjdT/el43MBzxSe5uJpCs/i3KYj8AcxKVqmcN1P9M5JOFqMNcT5lG3slMlfXGhZ6ZTPpSVFY2XF8GiXAvPMCfRxsZWpf3wlBNv+GKMlOOE098QKr7m97YIXsBCpDzrneZQTI5lI9tHrFDEU0I9A7qKjrnXV+j4JLXyLJ3hMUnyAgKNbNeV2rnQrRvw/3m9Svsmrn/ozWMdvc9uLUZHXojiQbGPwhy2Ycw0lheIv0F25sQSqS0UicVf63wNhy3NC7u11Pm2p9HO2qKpe2xvG5E/VS2v6Z8XErm4D3HWdoA20d4ljOU1UNTnP1HW04Xs0QjVs9CniX/1zdsNIHWV+wE74tjDVPyyF/kh4ptbf/Rt7FPksZe3eyd/YLGHf/lejo59zL+HRRkjsaA1CYzpg9NSzeSIX/MROwsV2pcRtboCnrX8L+PpbkDOor/ku96x2qj52gKi32atuKeYja+m6+3rDPbgl6XWTCUCcxfB9FZ/5JpHeCOFqKQE1O3KKODT3wrEaeWfWXWoawynwLnd/020i7oEUOBTX6z+ViONBzLkM71Boa3iVLToB/6AjbmFd3tv7KLxAqutP8emI2efrn0eDh3R0bZJ8oCy01d6jFEllIFYI/t7e8u/iPWbFKx8Shn7whgH0BFR8+KbvfCxLlmg7v4lpCEr7ucE9YZDydXaDGN37G3W5Gn3yt/0LApIh11gr+Zp82jIgdmGfhOErSop7/c/b0mndk4XCK2SICYbtLZ74FnRV",
        }

        config_str = "\n".join(f"{k!s}='{v!s}'" for k, v in config.items())
        multipass.write_file("pi-gen/config", config_str)

        logging.info("Starting disk image build")
        _start_time = time.time()
        multipass.cmd("./build.sh", cwd="pi-gen", pipe=False)
        _end_time = time.time()
        logging.info(f"Finished in {_end_time - _start_time:.3f}")
        print()
