from dataclasses import dataclass, field, asdict
from typing import List, Optional
from models.cloud_init.cloud_init import CloudInitObj
from utils.ssh import get_dev_pkey
from passlib.hash import md5_crypt
from paramiko import PKey

import yaml


@dataclass
class User:
    name: str = field(default="debian")
    lock_passwd: Optional[bool] = field(default=False)
    hashed_passwd: Optional[str] = field(default=None)
    ssh_authorized_keys: Optional[List[str]] = field(default=None)
    sudo: Optional[List[str]] = field(default=None)
    groups: Optional[str] = field(default=None)
    shell: str = field(default="/bin/bash")

    @property
    def password(self): ...

    @password.setter
    def password(self, new_pass: str):
        self.hashed_passwd = md5_crypt.hash(new_pass)

    def add_authorized_key(self, pem_key: PKey):
        if not self.ssh_authorized_keys:
            self.ssh_authorized_keys = []
        self.ssh_authorized_keys.append(f'{pem_key.name} {pem_key.get_base64()}')

@dataclass
class UserData(CloudInitObj):
    _FILENAME = 'user-data'

    users: List[User] = field(default_factory=list)

    package_update: Optional[bool] = field(default=True)
    package_upgrade: Optional[bool] = field(default=True)
    packages: Optional[List[str]] = field(default=None)

    runcmd: Optional[List[str]] = field(default=None)

    @classmethod
    def create_default(cls, pem_key: Optional[PKey] = None):
        default_user = User(
            name="kim",
            lock_passwd=False,
            sudo=["ALL=(ALL) NOPASSWD:ALL"],
            groups="users, sudo",
            shell="/bin/bash",
        )

        default_user.password = 'possible'

        if pem_key:
            default_user.add_authorized_key(pem_key)
        else:
            default_user.add_authorized_key(get_dev_pkey())

        return cls(
            users=[default_user],
            package_update=True,
            package_upgrade=True,
            packages=["qemu-guest-agent"],
            runcmd=["systemctl enable --now qemu-guest-agent.service"],
        )

    def to_yaml(self) -> str:
        return f"#cloud-config\n\n{yaml.safe_dump(asdict(self))}"
