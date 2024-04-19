import logging
from io import BytesIO
from typing import IO
import pycdlib
from pathlib import Path
from models.cloud_init.cloud_init import CloudInitObj


class CiData:
    # TODO: condider merging the CiData volume into the golden image
    # this should allow for using `genericcloud` debian image flavors

    def __init__(self, *ci_objects: CloudInitObj, iso_volume_id: str = "cidata"):
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

        for ci_object in ci_objects:
            self.add_ci_obj(ci_object)

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
        _last_percentage = 0
        def progress_cb(done: float, total: float):
            nonlocal _last_percentage
            _cur = done/total*100
            if _cur - _last_percentage >= 33:
                logging.debug(f"writing CiData ISO image: {_cur:0.2f}%")
                _last_percentage = _cur

        self._file_object = BytesIO()

        self.iso.write_fp(
            self._file_object,
            progress_cb=progress_cb,
        )

        self.iso.close()
        self._file_object.seek(0)

    @property
    def file_object(self):
        return self._file_object
