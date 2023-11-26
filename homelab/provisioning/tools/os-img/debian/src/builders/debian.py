import os
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
    with Multipass(target_config_name, multipass_auth) as multipass:
        """
        https://stackoverflow.com/questions/59940351/how-to-mount-a-memory-filesystem-onto-a-directory
        """

        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd("apt-get -y install genisoimage xorriso isolinux udevil")

        if os.path.isfile(f".cache/{iso_filename}"):
            logging.info("Found a cached .iso file, uploading to builder")
            multipass.upload(f".cache/{iso_filename}")
        else:
            multipass.cmd(f"wget {iso_url}")
            multipass.download(iso_filename, ".cache")

        multipass.cmd(f"udevil mount {iso_filename} /media/root/{iso_filename}")
        multipass.cmd(f"cp -rT /media/root/{iso_filename} isofiles/")
        multipass.cmd("chmod +w -R isofiles/install.amd/")
        multipass.cmd("gunzip isofiles/install.amd/initrd.gz")

        _template_files = [
            "preseed.cfg",
            "preseed-setup.sh",
            "firstboot-setup.sh",
            "firstboot.service",
            "qemu.conf",
        ]

        for fname in _template_files:
            multipass.upload_rendered_template(f"{fname}.j2")
            multipass.cmd(
                "cpio -H newc -o -A -F isofiles/install.amd/initrd", stdin=fname
            )

        multipass.cmd("gzip isofiles/install.amd/initrd")
        multipass.cmd("chmod -w -R isofiles/install.amd/")
        multipass.cmd("chmod +w md5sum.txt", cwd="isofiles")
        multipass.cmd(
            "find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt",
            cwd="isofiles",
        )
        multipass.cmd("chmod -w md5sum.txt", cwd="isofiles")
        multipass.cmd(
            "xorriso -as mkisofs "
            f"-o {target_iso_filename} "
            "-isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin "
            "-c isolinux/boot.cat "
            "-b isolinux/isolinux.bin "
            "-no-emul-boot "
            "-boot-load-size 4 "
            "-boot-info-table "
            "isofiles"
        )
        multipass.cmd("chmod +w -R isofiles")
        multipass.cmd("rm -r isofiles")
        multipass.cmd(f"udevil unmount /media/root/{iso_filename}")
        multipass.download(target_iso_filename, ".out")
