import datetime
import io
import json
import logging
import time
import uuid
from os import PathLike
from pathlib import Path
from typing import Optional, Dict, IO, Union

import random
import libvirt
import paramiko
from libvirt import virDomain, VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT

from models.cloud_init.metadata import MetaData
from models.cloud_init.userdata import UserData
from models.libvirt.snapshot import DomainSnapshot, Name, Description
from utils.dump import stderr_redirected
from utils.ssh import connect_ssh, connect_sftp, upload_file_path, upload_file_object
from utils.cidata import CiData
from models.libvirt.domain import *


def get_random_mac_address():
    # TODO: this raised an `libvirt: Domain Config error : XML error: expected unicast mac address, found multicast '5f:9d:70:a6:67:a6'` exception
    # TODO: read on mac address types

    # return ':'.join([hex(random.randint(0, 255))[2:].zfill(2) for _ in range(6)])
    return "00:00:00:{}:{}:{}".format(
        *[hex(random.randint(0, 255))[2:].zfill(2) for _ in range(3)]
    )


class Domain(virDomain):
    def __init__(
        self,
        vd: virDomain,
        userdata: Optional[UserData] = None,
        metadata: Optional[MetaData] = None,
    ):
        self._proxied = vd
        self._wait_for_qemu_ga(delay=10)

        self.userdata: UserData = userdata
        self.metadata: MetaData = metadata

    def __getattr__(self, name: str):
        return getattr(self._proxied, name)

    @classmethod
    def create_default(
        cls, conn: libvirt.virConnect, memory: int = 2097152, vcpus: int = 2
    ):
        machine_name = f"debby-auto-{uuid.uuid4()!s}"
        source_img_file = Path(f"/root/workspace/{machine_name}.qcow2").as_posix()
        cidata_filepath = Path("/root/workspace/cidata.iso").as_posix()

        userdata = UserData.create_default()
        metadata = MetaData(machine_name, machine_name[:15])

        with connect_ssh("root", "nuc.local") as ssh_client:
            ssh_client.exec_command(
                f"cp /root/workspace/.cache/debby-generic-11.qcow2 {source_img_file}"
            )

            with connect_sftp(ssh_client) as stfp_client:
                ci_data = CiData()
                ci_data.add_ci_obj(userdata)
                ci_data.add_ci_obj(metadata)
                ci_data.build()

                stfp_client.putfo(ci_data.file_object, "/root/workspace/cidata.iso")

        _vd = conn.createXML(
            LibvirtDomain(
                type="kvm",
                id="1",
                name=DomainName(machine_name),
                metadata=Metadata(Libosinfo(Os2(id="http://debian.org/debian/11"))),
                memory=Memory(unit="KiB", value=str(memory)),
                vcpu=Vcpu(placement="static", value=str(vcpus)),
                resource=Resource(ResourcePartition("/machine")),
                os=Os1(TypeType("x86_64", "pc-q35-7.2", "hvm"), Boot("hd")),
                features=Features(Acpi(), Apic(), Vmport("off")),
                cpu=Cpu("host-passthrough", "none", "on"),
                clock=Clock(
                    offset="utc",
                    timers=[
                        Timer("rtc", tickpolicy="catchup"),
                        Timer("pit", tickpolicy="delay"),
                        Timer("hpet", present="no"),
                    ],
                ),
                on_poweroff=OnPoweroff("destroy"),
                on_reboot=OnReboot("restart"),
                on_crash=OnCrash("destroy"),
                pm=Pm(SuspendToMem("no"), SuspendToDisk("no")),
                devices=Devices(
                    Emulator("/usr/bin/qemu-system-x86_64"),
                    [
                        Disk(
                            type="file",
                            device="disk",
                            driver=Driver(name="qemu", type="qcow2"),
                            source=Source(file=source_img_file, index="2"),
                            backing_store=BackingStore(),
                            target=Target(dev="vda", bus="virtio"),
                            alias=Alias(name="virtio-disk0"),
                            address=Address(
                                type="pci",
                                domain="0x0000",
                                bus="0x04",
                                slot="0x00",
                                function="0x0",
                            ),
                        ),
                        Disk(
                            type="file",
                            device="cdrom",
                            driver=Driver("qemu", "raw"),
                            source=Source(file=cidata_filepath, index="1"),
                            backing_store=BackingStore(),
                            target=Target(dev="sda", bus="sata"),
                            readonly=ReadOnly(),
                            alias=Alias(name="sata0-0-0"),
                            address=Address(
                                type="drive",
                                controller="0",
                                bus="0",
                                target="0",
                                unit="0",
                            ),
                        ),
                    ],
                    Interface(
                        type="network",
                        mac=Mac(get_random_mac_address()),
                        source=Source(
                            network="default",
                            portid="bbbd2004-3294-4ecd-a1cc-f43d4f3c26a0",  # should this be unique?
                            bridge="virbr0",
                        ),
                        target=Target(dev="vnet0"),
                        model=Model(type="virtio"),
                        alias=Alias(name="net0"),
                        address=Address(
                            type="pci",
                            domain="0x0000",
                            bus="0x01",
                            slot="0x00",
                            function="0x0",
                        ),
                    ),
                    Serial(
                        type="pty",
                        source=Source(path="/dev/pts/2"),
                        target=Target("isa-serial", "0", Model(name="isa-serial")),
                        alias=Alias(name="serial0"),
                    ),
                    Console(
                        type="pty",
                        tty="/dev/pty/2",
                        source=Source(path="/dev/pts/2"),
                        target=Target("serial", "0"),
                        alias=Alias(name="serial0"),
                    ),
                    Graphics(
                        type="spice",
                        port="5900",
                        autoport="yes",
                        listen_attribute="127.0.0.1",
                        listen=Listen("address", "127.0.0.1"),
                        image=Image("off"),
                    ),
                    Sound(
                        model="ich9",
                        alias=Alias(name="sound0"),
                        address=Address(
                            type="pci",
                            domain="0x0000",
                            bus="0x00",
                            slot="0x1b",
                            function="0x0",
                        ),
                    ),
                    Audio(id="1", type="spice"),
                    Video(
                        model=Model(type="virtio", heads="1", primary="yes"),
                        alias=Alias(name="video0"),
                        address=Address(
                            type="pci",
                            domain="0x0000",
                            bus="0x00",
                            slot="0x01",
                            function="0x0",
                        ),
                    ),
                    Memballoon(
                        model="virtio",
                        alias=Alias(name="balloon0"),
                        address=Address(
                            type="pci",
                            domain="0x0000",
                            bus="0x05",
                            slot="0x00",
                            function="0x0",
                        ),
                    ),
                    Rng(
                        model="virtio",
                        backend=Backend(model="random", value="/dev/urandom"),
                        alias=Alias(name="rng0"),
                        address=Address(
                            type="pci",
                            domain="0x0000",
                            bus="0x06",
                            slot="0x00",
                            function="0x0",
                        ),
                    ),
                    Channel(
                        type="unix",
                        target=Target(
                            type="virtio",
                            name="org.qemu.guest_agent.0",
                        ),
                    ),
                ),
                seclabels=[
                    Seclabel(type="dynamic", model="apparmor", relabel="yes"),
                    Seclabel(
                        type="dynamic",
                        model="dac",
                        relabel="yes",
                        label=SeclabelLabel("+0:+0"),
                        imagelabel=SeclabelImageLabel("+0:+0"),
                    ),
                ],
            ).to_xml_string()
        )

        return cls(_vd, userdata, metadata)

    def _wait_for_qemu_ga(self, tries: int = 50, delay: int = 5):
        # TODO: consider using this as a decorator like `ensure_ga`

        for i in range(tries):
            try:
                with stderr_redirected():
                    self.hostname(libvirt.VIR_DOMAIN_GET_HOSTNAME_AGENT)
                return
            except Exception as e:
                if "err" in dir(e) and e.err[0] != libvirt.VIR_ERR_AGENT_UNRESPONSIVE:
                    raise e

                logging.debug(
                    f"[{i+1}/{tries}] waiting for qemu-guest-agent to start..."
                )
                time.sleep(delay)

        logging.error("qemu-user-agent didn't start on time")
        raise libvirt.libvirtError("Qemu Guest Agent didn't start on time")

    def ip(self) -> Optional[str]:
        addresses = self.interfaceAddresses(VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
        for addr in addresses["enp1s0"]["addrs"]:
            if addr["type"] == 0:  # address type ipv4
                return addr["addr"]

        logging.error("couldn't find machine ip address")
        return None

    def connect_ssh(self) -> paramiko.SSHClient:
        return connect_ssh(
            self.userdata.users[0].name,
            self.ip(),
            gateway_user="root",
            gateway="nuc.local",
        )

    def exec_ssh_cmd(
        self, cmd: str, env: Optional[Dict[str, str]] = None, ignore_error: bool = False
    ) -> str:
        with self.connect_ssh() as ssh_client:
            _, stdout, stderr = ssh_client.exec_command(cmd, environment=env)
            _stderr = stderr.read().strip()
            if len(_stderr) > 0 and not ignore_error:
                raise paramiko.SSHException(str(_stderr, "utf-8"))

            return str(stdout.read(), "utf-8").strip()

    def upload_file(self, src: Union[str, IO, PathLike], dest: str):
        if isinstance(src, str):
            return upload_file_path(
                src,
                dest,
                self.userdata.users[0].name,
                self.ip(),
                gateway_user="root",
                gateway="nuc.local",
            )
        elif isinstance(src, io.IOBase):
            return upload_file_object(
                src,
                dest,
                self.userdata.users[0].name,
                self.ip(),
                gateway_user="root",
                gateway="nuc.local",
            )
        else:
            raise Exception(f"Wrong argument type: {type(src)}")

    def download_file(self, src: str, dest: str):
        with self.connect_ssh() as ssh_client:
            stfp_client = ssh_client.open_sftp()
            if stfp_client is None:
                raise paramiko.SSHException("Couldn't create an SFTP client")

            def progress(sent: int, total: int):
                logging.debug(f"[{sent}/{total}] Downloading file {src}")

            stfp_client.get(
                src, dest, callback=progress
            )  # TODO: handle dest directories
            stfp_client.close()

    def create_snapshot(self) -> libvirt.virDomainSnapshot:
        _uuid = str(uuid.uuid4())
        return self.snapshotCreateXML(
            DomainSnapshot(
                name=Name(_uuid),
                description=Description(
                    json.dumps(
                        {
                            "date": str(datetime.datetime.now()),
                            "name": _uuid,
                        }
                    )
                ),
            ).to_xml_string(),
            libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC,
        )
