from dataclasses import dataclass
from typing import Optional, List
from models.libvirt.domain import LibvirtDomain


@dataclass
class Host:
    ip: int
    domains: List[LibvirtDomain]

    def __init__(self):
        ...
