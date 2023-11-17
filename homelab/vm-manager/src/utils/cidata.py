import fnmatch
import os
import sys
import time
import logging
from io import BytesIO
from typing import Dict, IO, Union
import pycdlib
from pathlib import Path
from models.cloud_init.cloud_init import CloudInitObj


class CiData:
    def __init__(self, iso_volume_id: str = "cidata"):
        self.iso_volume_id = iso_volume_id

        self.iso = pycdlib.PyCdlib()
        self.iso.new(
            interchange_level=1,
            vol_ident=self.iso_volume_id,
            joliet=3,
            rock_ridge="1.09",
            vol_set_ident="",
        )

        self._file_object = None

    def add_ci_obj(self, obj: CloudInitObj):
        file_bytes = bytes(obj.to_yaml(), 'utf-8')
        self.add_file(BytesIO(file_bytes), obj._FILENAME, len(file_bytes))

    def add_file(self, fo: IO, file_name: str, file_size: int):
        self.iso.add_fp(
            fo,
            file_size,
            joliet_path=Path("/", file_name[:64]).as_posix(),
            iso_path=Path(
                "/", ".".join(pycdlib.utils.mangle_file_for_iso9660(file_name, 1))
            ).as_posix(),
            rr_name=file_name,
        )

    def build(self):
        class ProgressData:
            def __init__(self):
                self.last_percent = 0.0

        def progress_cb(done: float, total: float, progress_data: ProgressData):
            percent = "%.2f%%" % (done / total * 100)
            if percent != progress_data.last_percent:
                logging.debug(f"writing ISO image: {percent:7}")
                progress_data.last_percent = percent

        self._file_object = BytesIO()

        self.iso.write_fp(
            self._file_object,
            progress_cb=progress_cb,
            progress_opaque=ProgressData()
        )
        self.iso.close()

        self._file_object.seek(0)

    @property
    def file_object(self):
        return self._file_object
