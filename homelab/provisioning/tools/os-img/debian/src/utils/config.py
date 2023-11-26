import os
from functools import cached_property
import yaml
import collections.abc
from utils.models.config import Config

class ConfigException(Exception): ...

def get_config(config: str) -> Config:
    if config == 'nuc':
        from utils.configs.nuc import NucConfig
        return NucConfig()
    elif config == 'thinkpad':
        from utils.configs.thinkpad import ThinkpadConfig
        return ThinkpadConfig()
    else:
        raise ConfigException(f'No config implemented for {config_name}')
