import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class User:
    name: str = field(default='debian')
    lock_passwd: Optional[bool] = field(default=False)
    hashed_passwd: Optional[str] = field(default=None)
    ssh_authorized_keys: Optional[List[str]] = field(default=None)
    sudo: Optional[List[str]] = field(default=None)
    groups: Optional[str] = field(default=None)
    shell: str = field(default='/bin/bash')


@dataclass
class UserData:
    users: List[User] = field(default_factory=list)

    package_update: Optional[bool] = field(default=True)
    package_upgrade: Optional[bool] = field(default=True)
    packages: Optional[List[str]] = field(default=None)

    runcmd: Optional[List[str]] = field(default=None)

    def to_yaml(self) -> str:
        return f'#cloud-config\n\n{yaml.safe_dump(asdict(self))}'
