import os
import logging
from utils import Multipass

if __name__ == "__main__":
    ISO_FILENAME = os.environ["DEBIAN_ISO_FILENAME"]
    ISO_URL = os.environ["DEBIAN_ISO_URL"]
    FLASH_TARGET_CONFIG_FILE = os.environ["FLASH_TARGET_CONFIG_FILE"]
    PRESEEDED_ISO_FILENAME = os.environ["PRESEEDED_ISO_FILENAME"]

    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

    with Multipass(FLASH_TARGET_CONFIG_FILE) as multipass:
        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd("apt-get -y install genisoimage xorriso isolinux udevil")

        if os.path.isfile(f".cache/{ISO_FILENAME}"):
            logging.info("Found a cached .iso file, uploading to builder")
            multipass.upload(f".cache/{ISO_FILENAME}")
        else:
            multipass.cmd(f"wget {ISO_URL}")
            multipass.download(ISO_FILENAME, ".cache")

        multipass.cmd(f"udevil mount {ISO_FILENAME} /media/root/{ISO_FILENAME}")
        multipass.cmd(f"cp -rT /media/root/{ISO_FILENAME} isofiles/")
        multipass.cmd("chmod +w -R isofiles/install.amd/")
        multipass.cmd("gunzip isofiles/install.amd/initrd.gz")

        multipass.upload_rendered_template("preseed.cfg.j2")
        multipass.upload_rendered_template("setup.sh.j2")

        multipass.cmd(
            "cpio -H newc -o -A -F isofiles/install.amd/initrd", stdin="preseed.cfg"
        )
        multipass.cmd(
            "cpio -H newc -o -A -F isofiles/install.amd/initrd", stdin="setup.sh"
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
            f"xorriso -as mkisofs -o {PRESEEDED_ISO_FILENAME} -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin -c isolinux/boot.cat -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table isofiles",
        )
        multipass.cmd("chmod +w -R isofiles")
        multipass.cmd("rm -r isofiles")
        multipass.cmd(f"udevil unmount /media/root/{ISO_FILENAME}")
        multipass.download(PRESEEDED_ISO_FILENAME, ".out")
