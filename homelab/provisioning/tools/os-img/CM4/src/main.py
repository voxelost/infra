import contextlib
import os
import dmglib
import tempfile
import shutil
import libarchive
import io
from pyzstd import compress_stream, decompress_stream
import logging


from libarchive import _libarchive


@contextlib.contextmanager
def disk_image(filepath: str, mountpoint: str) -> dmglib.DiskImage:
    img = None
    _img_name = os.path.basename(filepath)
    try:
        logging.debug(f"mounting disk image {_img_name} at {mountpoint}")
        img = dmglib.DiskImage(filepath)
        img.attach(mountpoint)
        yield
    finally:
        if img:
            logging.debug(f"unmounting disk image {_img_name}")
            img.detach()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    with tempfile.TemporaryDirectory() as isofiles:
        with tempfile.TemporaryDirectory() as mountpoint:
            with disk_image("resources/20230612_raspi_4_bookworm.img", mountpoint):
                for fname in os.listdir(mountpoint):
                    logging.debug(f"copying {fname} to {isofiles}")
                    # this assumes no directories are present in the source folder
                    shutil.copy2(
                        os.path.join(mountpoint, fname),
                        os.path.join(isofiles, fname),
                    )

        initdr_img_path = os.path.join(isofiles, "initrd.img-6.1.0-9-arm64")
        initdr_path = os.path.join(isofiles, "initrd")

        with io.open(initdr_img_path, "rb") as ifh:
            with io.open(initdr_path, "wb") as ofh:
                logging.debug(f"decompressing {initdr_img_path} into {initdr_path}")
                decompress_stream(ifh, ofh)

        # test
        with libarchive.Archive(initdr_path, "r", format="cpio") as archive:
            _BLOCK_SIZE = archive.blocksize
            assert all(
                "preseed.cfg" not in path for path in archive.iterpaths()
            ), "preseed.cfg found in the archive before injecting"

        a = _libarchive.archive_read_new()
        _libarchive.archive_read_support_format_cpio(a)
        # _libarchive.archive_read_support_filter_none(a)
        with open(initdr_path, "r") as fptr:
            while True:
                _libarchive.archive_read_open_fd(a, fptr.fileno(), _BLOCK_SIZE)
                e = _libarchive.archive_entry_new()
                try:
                    res = _libarchive.archive_read_next_header2(a, e)
                    print(
                        res,
                        res == _libarchive.ARCHIVE_EOF,
                        _libarchive.archive_error_string(a),
                    )
                    if res == _libarchive.ARCHIVE_EOF:
                        break
                # except Exception as _e:
                #     print(_e)
                finally:
                    _libarchive.archive_entry_free(e)

        # with libarchive.Archive(initdr_path, "w", format="cpio") as archive:
        #     # TODO: fill the jinja template
        #     logging.debug("injecting preseed.cfg file into the archive")
        #     archive.writepath("resources/preseed.cfg.jinja2", pathname="/preseed.cfg")

        # test
        with libarchive.Archive(initdr_path, "r", format="cpio") as archive:
            # why file not in archive :(
            try:
                assert any(
                    "preseed.cfg" in path for path in archive.iterpaths()
                ), "preseed.cfg not found anywhere in the archive"

                assert any(
                    "preseed.cfg" in archive.iterpaths()
                ), "preseed.cfg not found in archive root"
            except Exception as e:
                logging.error(e)

        with io.open(initdr_path, "rb") as ifh:
            with io.open(initdr_img_path, "wb") as ofh:
                logging.debug(f"compressing {initdr_path} back into {initdr_img_path}")
                compress_stream(ifh, ofh)

        logging.debug(f"isofiles: {isofiles}")
        logging.debug("")
    # unzst initrd.img-6.1.0-9-arm64 -o initdr
    # echo preseed.cfg | cpio --format newc --create -A --file <unpacked initdr>
