from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from passlib.hash import md5_crypt

@dataclass
class User:
    name: str = field(default='debian')
    password: str = field(default='debian')
    password_hash: Optional[str] = field(default=None, init=False)
    libvirt_user: bool = field(default=True)
    authorized_keys: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._update_password_hash()

    def _update_password_hash(self) -> str:
        self.password_hash = str(md5_crypt.hash(self.password))

    def set_password(self, password: str):
        self.password = password
        self._update_password_hash()

@dataclass
class Script:
    location: str = field(default='/nonexistent/path')
    additional_steps: List[str] = field(default_factory=list)

@dataclass
class NetworkInterface:
    name: str = field(default='noname')
    creation_steps: List[str] = field(default_factory=list)

@dataclass
class NetworkConfig:
    interfaces: List[NetworkInterface] = field(default_factory=list)
    # ip_interfaces = List[NetworkInterface] = field(default_factory=lambda: [
    #     NetworkInterface('bridge0', creation_steps=[
    #         "ip link add name {{ network.bridge_name }} type bridge",
    #         "ip link set {{ network.ethernet_interface_id }} up",
    #         "ip link set {{ network.ethernet_interface_id }} master {{ network.bridge_name }}",
    #         # add static ip address to bridge
    #         "ip address add dev {{ network.bridge_name }} {{ network.cidr_range }}",
    #     ]),
    # ])
    # ip_interfaces = List[NetworkInterface] = field(default_factory=lambda: [
    #     NetworkInterface('macvtap0', creation_steps=[
    #         # load required kernel module
    #         "lsmod | grep macvlan || modprobe macvlan",
    #         "ip link add link {{ network.ethernet_interface_id }} name {{ network.macvtap_name }} type macvtap mode bridge",
    #         "ip link set {{ network.macvtap_name }} up",
    #     ]),
    # ])

    ethernet_interface_id: str = field(default='enp3s0')
    cidr_range: str = field(default="192.168.1.80/28")

@dataclass
class QemuUser:
    name: str = field(default='root')
    group: str = field(default='root')

@dataclass
class QemuConfig:
    user: QemuUser = field(default_factory=QemuUser)

@dataclass
class AptConfig:
    packages: List[str] = field(default_factory=lambda: [
        "openssh-server",
        "avahi-daemon",
        "sudo",
        "build-essential",
        "zlib1g-dev",
        "libncurses5-dev",
        "libgdbm-dev",
        "libnss3-dev",
        "libssl-dev",
        "libreadline-dev",
        "libffi-dev",
        "libsqlite3-dev",
        "wget",
        "libbz2-dev",
        "python3",
        # "qemu-kvm",
        "libvirt-clients",
        "bridge-utils",
        "libvirt-daemon-system",
        # "qemu-efi",

        # dev packages
        "virt-manager",

        # secureboot packages # TODO
        # "ovmf",
        # "qemu-system-x86",
        # "gpg",
        # "debian-keyring",
    ])
    update: bool = field(default=True)
    upgrade: bool = field(default=True)

@dataclass
class Config:
    hostname: str = field(default='hostname')
    root_user: User = field(default_factory=lambda: User(
        name='root',
        password='root',
        authorized_keys=[
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAD9QD3Ktvnq5P9oa4XxZ/h1tSAQnGdZkjAxCU0jlZ1UsWp9hf0/vRLlvHa6B6xaaaZZfaIuUkh3Y+y6obRbul+SZ1ru8ixj+KJkl0b0ZL20PJ0lbN3n8IiE1x53xCsXkjt0F7GHVmzUMuyguff0bnCd2Nf6O0u6ja0766NwJ5G565lBkZT7Q4u38+XZSFH4r9F9emWZxEF9EfteF8LqyLlCDAcrPDbe6iqhXqjUlTD6uNORMKh1i1U49yB6khNcy2rwJYuIFtd0KSqShhHBkWGdrsUnjN7KEEuc0ORvfryJDaEcIoqodXcYbHH2W0gE4DHl71n4l2/XKg5z1NzUWcxcJWSnmfwTkynVFqpdAm0hz+54andsya9exHbgWkqsoaZx/ecZNUySoIgnQGXp+yGUg6q0DwVDA4EdWhlmwSpJ+EU6tozzaxsRK7mZZTpC4sz/wnJNb5itjAS2vd3wxslPRliIyQFvNrNc5bGY9G4ECA6+CbVh8KexSNZD08udypiVO875TZM0WUbN+TmTtjfMAcdfYji0ZNRMv02nnMkll754KKe9BplzAjNYKy7ol3rb9/shA/aoihEi7pLhUEl6jjdT/el43MBzxSe5uJpCs/i3KYj8AcxKVqmcN1P9M5JOFqMNcT5lG3slMlfXGhZ6ZTPpSVFY2XF8GiXAvPMCfRxsZWpf3wlBNv+GKMlOOE098QKr7m97YIXsBCpDzrneZQTI5lI9tHrFDEU0I9A7qKjrnXV+j4JLXyLJ3hMUnyAgKNbNeV2rnQrRvw/3m9Svsmrn/ozWMdvc9uLUZHXojiQbGPwhy2Ycw0lheIv0F25sQSqS0UicVf63wNhy3NC7u11Pm2p9HO2qKpe2xvG5E/VS2v6Z8XErm4D3HWdoA20d4ljOU1UNTnP1HW04Xs0QjVs9CniX/1zdsNIHWV+wE74tjDVPyyF/kh4ptbf/Rt7FPksZe3eyd/YLGHf/lejo59zL+HRRkjsaA1CYzpg9NSzeSIX/MROwsV2pcRtboCnrX8L+PpbkDOor/ku96x2qj52gKi32atuKeYja+m6+3rDPbgl6XWTCUCcxfB9FZ/5JpHeCOFqKQE1O3KKODT3wrEaeWfWXWoawynwLnd/020i7oEUOBTX6z+ViONBzLkM71Boa3iVLToB/6AjbmFd3tv7KLxAqutP8emI2efrn0eDh3R0bZJ8oCy01d6jFEllIFYI/t7e8u/iPWbFKx8Shn7whgH0BFR8+KbvfCxLlmg7v4lpCEr7ucE9YZDydXaDGN37G3W5Gn3yt/0LApIh11gr+Zp82jIgdmGfhOErSop7/c/b0mndk4XCK2SICYbtLZ74FnRV",
        ],
    ))
    users: List[User] = field(default_factory=lambda: [
        User(
            authorized_keys=[
                "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAD9QD3Ktvnq5P9oa4XxZ/h1tSAQnGdZkjAxCU0jlZ1UsWp9hf0/vRLlvHa6B6xaaaZZfaIuUkh3Y+y6obRbul+SZ1ru8ixj+KJkl0b0ZL20PJ0lbN3n8IiE1x53xCsXkjt0F7GHVmzUMuyguff0bnCd2Nf6O0u6ja0766NwJ5G565lBkZT7Q4u38+XZSFH4r9F9emWZxEF9EfteF8LqyLlCDAcrPDbe6iqhXqjUlTD6uNORMKh1i1U49yB6khNcy2rwJYuIFtd0KSqShhHBkWGdrsUnjN7KEEuc0ORvfryJDaEcIoqodXcYbHH2W0gE4DHl71n4l2/XKg5z1NzUWcxcJWSnmfwTkynVFqpdAm0hz+54andsya9exHbgWkqsoaZx/ecZNUySoIgnQGXp+yGUg6q0DwVDA4EdWhlmwSpJ+EU6tozzaxsRK7mZZTpC4sz/wnJNb5itjAS2vd3wxslPRliIyQFvNrNc5bGY9G4ECA6+CbVh8KexSNZD08udypiVO875TZM0WUbN+TmTtjfMAcdfYji0ZNRMv02nnMkll754KKe9BplzAjNYKy7ol3rb9/shA/aoihEi7pLhUEl6jjdT/el43MBzxSe5uJpCs/i3KYj8AcxKVqmcN1P9M5JOFqMNcT5lG3slMlfXGhZ6ZTPpSVFY2XF8GiXAvPMCfRxsZWpf3wlBNv+GKMlOOE098QKr7m97YIXsBCpDzrneZQTI5lI9tHrFDEU0I9A7qKjrnXV+j4JLXyLJ3hMUnyAgKNbNeV2rnQrRvw/3m9Svsmrn/ozWMdvc9uLUZHXojiQbGPwhy2Ycw0lheIv0F25sQSqS0UicVf63wNhy3NC7u11Pm2p9HO2qKpe2xvG5E/VS2v6Z8XErm4D3HWdoA20d4ljOU1UNTnP1HW04Xs0QjVs9CniX/1zdsNIHWV+wE74tjDVPyyF/kh4ptbf/Rt7FPksZe3eyd/YLGHf/lejo59zL+HRRkjsaA1CYzpg9NSzeSIX/MROwsV2pcRtboCnrX8L+PpbkDOor/ku96x2qj52gKi32atuKeYja+m6+3rDPbgl6XWTCUCcxfB9FZ/5JpHeCOFqKQE1O3KKODT3wrEaeWfWXWoawynwLnd/020i7oEUOBTX6z+ViONBzLkM71Boa3iVLToB/6AjbmFd3tv7KLxAqutP8emI2efrn0eDh3R0bZJ8oCy01d6jFEllIFYI/t7e8u/iPWbFKx8Shn7whgH0BFR8+KbvfCxLlmg7v4lpCEr7ucE9YZDydXaDGN37G3W5Gn3yt/0LApIh11gr+Zp82jIgdmGfhOErSop7/c/b0mndk4XCK2SICYbtLZ74FnRV",
            ],
        )
    ])
    script: Dict[str, Script] = field(default_factory=lambda: {
        'preseed': Script(location='/root/preseed-setup.sh'),
        'firstboot': Script(location='/root/firstboot-setup.sh'),
    })
    network: NetworkConfig = field(default_factory=NetworkConfig)
    qemu: QemuConfig = field(default_factory=QemuConfig)
    apt: AptConfig = field(default_factory=AptConfig)
    debug: bool = field(default=False)

    def as_dict(self) -> dict:
        return asdict(self)
