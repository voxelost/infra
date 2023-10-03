import os
import logging
from utils import Multipass


ISO_FILENAME = "debian-12.1.0-amd64-netinst.iso"
ISO_URL = (
    f"http://ftp.icm.edu.pl/pub/Linux/debian-cd/12.1.0/amd64/iso-cd/{ISO_FILENAME}"
)

if __name__ == "__main__":
    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

    with Multipass() as multipass:
        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd("apt-get -y install genisoimage xorriso isolinux udevil")

        if os.path.isfile(f".cache/{ISO_FILENAME}"):
            logging.info("Found a cached .iso file, uploading to builder")
            multipass.upload(f".cache/{ISO_FILENAME}")
        else:
            multipass.cmd(f"wget {ISO_URL}")
            multipass.download(ISO_FILENAME, f".cache/{ISO_FILENAME}")
        multipass.cmd(f"udevil mount {ISO_FILENAME} /media/root/{ISO_FILENAME}")
        multipass.cmd(f"cp -rT /media/root/{ISO_FILENAME} isofiles/")
        multipass.cmd("chmod +w -R isofiles/install.amd/")
        multipass.cmd("gunzip isofiles/install.amd/initrd.gz")
        multipass.upload(
            "resources/preseed.cfg",
            "preseed.cfg",
        )
        multipass.cmd(
            "cpio -H newc -o -A -F isofiles/install.amd/initrd", stdin="preseed.cfg"
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
            f"xorriso -as mkisofs -o preseeded-{ISO_FILENAME} -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin -c isolinux/boot.cat -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table isofiles",
        )
        multipass.cmd("chmod +w -R isofiles")
        multipass.cmd("rm -r isofiles")
        multipass.cmd(f"udevil unmount /media/root/{ISO_FILENAME}")
        multipass.download(f"preseeded-{ISO_FILENAME}")
