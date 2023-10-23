import os
from functools import cached_property
import yaml


class Config(dict):
    def __init__(
        self,
        config_file: os.PathLike,
        default_config_file: os.PathLike = "configs/defaults.yml",
        commons_config_file: os.PathLike = "configs/commons.yml",
    ):
        with open(default_config_file, "r") as fptr:
            self.update(yaml.safe_load(fptr))

        with open(commons_config_file, "r") as fptr:
            self.update(yaml.safe_load(fptr))

        with open(config_file, "r") as fptr:
            self.update(yaml.safe_load(fptr))
