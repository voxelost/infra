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
    args = parser.parse_args()

    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

    with Multipass(args.target_config_file, args.multipass_auth) as multipass:
        multipass.cmd("apt-get update")
        multipass.cmd("apt-get upgrade -y")
        multipass.cmd("apt-get -y install genisoimage xorriso isolinux udevil")

        if os.path.isfile(f".cache/{args.iso_filename}"):
            logging.info("Found a cached .iso file, uploading to builder")
            multipass.upload(f".cache/{args.iso_filename}")
        else:
            multipass.cmd(f"wget {args.iso_url}")
            multipass.download(args.iso_filename, ".cache")

        multipass.cmd(
            f"udevil mount {args.iso_filename} /media/root/{args.iso_filename}"
        )
        multipass.cmd(f"cp -rT /media/root/{args.iso_filename} isofiles/")
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
            f"xorriso -as mkisofs -o {args.target_iso_filename} -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin -c isolinux/boot.cat -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table isofiles",
        )
        multipass.cmd("chmod +w -R isofiles")
        multipass.cmd("rm -r isofiles")
        multipass.cmd(f"udevil unmount /media/root/{args.iso_filename}")
        multipass.download(args.target_iso_filename, ".out")
