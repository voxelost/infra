import os
from functools import cached_property
import yaml
import collections.abc


class Config(dict):
    def __init__(
        self,
        config_file: os.PathLike,
        default_config_file: os.PathLike = "configs/defaults.yml",
        commons_config_file: os.PathLike = "configs/commons.yml",
    ):
        if os.path.exists(default_config_file):
            with open(default_config_file, "r") as fptr:
                # update(self, yaml.safe_load(fptr))
                _update(self, yaml.safe_load(fptr))

        if os.path.exists(commons_config_file):
            with open(commons_config_file, "r") as fptr:
                # update(self, yaml.safe_load(fptr))
                _update(self, yaml.safe_load(fptr))

        with open(config_file, "r") as fptr:
            # update(self, yaml.safe_load(fptr))
            _update(self, yaml.safe_load(fptr))


def _update(self, other):
    for k, v in other.items():
        if isinstance(v, collections.abc.Mapping):
            self[k] = _update(self.get(k, {}), v)
        else:
            self[k] = v
    return self
