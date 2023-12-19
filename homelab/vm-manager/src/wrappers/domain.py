import datetime
import io
import json
import logging
import time
import uuid
from os import PathLike
from pathlib import Path
from typing import Optional, Dict, IO, Union
from io import StringIO

import random
import libvirt
import paramiko
from libvirt import virDomain, VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT

from models.cloud_init.metadata import MetaData
from models.cloud_init.userdata import UserData
from models.libvirt.snapshot import DomainSnapshot, Name, Description
from utils.dump import stderr_redirected, get_disk_image_details
from utils.ssh import connect_ssh, connect_sftp, upload_file_path, upload_file_object, get_nuc_pkey, get_dev_pem_keyname, get_dev_hostname
from utils.cidata import CiData
from models.libvirt.domain import *


class Domain(virDomain):
    def __init__(
        self,
        vd: virDomain,
        userdata: Optional[UserData] = None,
        metadata: Optional[MetaData] = None,
    ):
        self._proxied = vd
        try:
            self._wait_for_qemu_ga(tries=50, delay=10)
        except Exception as e:
            logging.error(e)

        self.userdata: UserData = userdata
        self.metadata: MetaData = metadata

    def __getattr__(self, name: str):
        return getattr(self._proxied, name)

    @classmethod
    def create_default(
        cls, conn: libvirt.virConnect, memory: int = 2097152, vcpus: int = 4
    ):
        machine_uuid = str(uuid.uuid1()).split('-')[0]
        machine_name =  machine_uuid
        workspace_path = Path('/root/workspace/machines', machine_uuid).as_posix()
        source_img_file = Path(workspace_path, f"{machine_name}.qcow2").as_posix()
        cidata_filepath = Path(workspace_path, "cidata.iso").as_posix()

        userdata = UserData.create_default()
        metadata = MetaData(machine_name, machine_name)

        logging.debug(f'machine uuid: {machine_uuid}')

        with connect_ssh("root", get_dev_hostname()) as ssh_client:
            ssh_client.exec_command(
                f"mkdir -p /root/workspace/machines {workspace_path}"
            )

            chosen_img = get_disk_image_details('debian', '11', 'generic', 'amd64')
            # chosen_img = get_disk_image_details('ubuntu', '22.04', 'kvm-optimised', 'amd64')
            DEBIAN_QCOW_FILENAME = chosen_img['filename']
            LIBOS_META = chosen_img['libos_meta']

            ssh_client.exec_command(
                f"cp /root/workspace/.cache/{DEBIAN_QCOW_FILENAME} {source_img_file}"
            )

            ssh_client.exec_command(
                f"cp /root/workspace/.cache/{get_dev_pem_keyname()} {workspace_path}"
            )

            with connect_sftp(ssh_client) as stfp_client:
                debug_data = {
                    'machine_uuid': machine_uuid,
                    'machine_name': machine_name,
                    'base_img_file': DEBIAN_QCOW_FILENAME,
                    'libos_meta': LIBOS_META,
                    'source_img_file': source_img_file,
                    'cidata_filepath': cidata_filepath,
                    'userdata': userdata.to_yaml(),
                    'metadata': metadata.to_yaml(),
                }

                with StringIO(json.dumps(debug_data, indent=2)) as debug_fo:
                    stfp_client.putfo(debug_fo, Path(workspace_path, 'debug_info.json').as_posix())

            ci_data = CiData(userdata, metadata)
            ci_data.build()

            with connect_sftp(ssh_client) as stfp_client:
                stfp_client.putfo(ci_data.file_object, cidata_filepath)

        _vd = conn.createXML(
            LibvirtDomain(
                type="kvm",
                name=Name(value=machine_name),
                metadata=Metadata(Libosinfo(os=Os2(id=LIBOS_META))),
                memory=Memory(
                    unit="KiB",
                    value=str(memory)
                ),
                vcpu=Vcpu(value=str(vcpus)),
                resource=Resource(partition=ResourcePartition("/machine")),
                os=Os1(
                    type=OsType(value="hvm"),
                    boot=Boot(dev="hd"),
                ),
                features=Features(
                    acpi=Acpi(),
                    apic=Apic(),
                    vmport=Vmport("off"),
                ),
                cpu=Cpu(mode="host-passthrough", check="none", migratable="on"),
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
                power_management=PowerManagement(
                    suspend_to_mem=SuspendToMem("no"),
                    suspend_to_disk=SuspendToDisk("no"),
                ),
                devices=Devices(
                    emulator=Emulator("/usr/bin/qemu-system-x86_64"),
                    disks=[
                        Disk(
                            type="file",
                            device="disk",
                            driver=Driver(name="qemu", type="qcow2"),
                            source=Source(file=source_img_file),
                            # backing_store=BackingStore(),
                            target=Target(dev="vda", bus="virtio"),
                        ),
                        Disk(
                            type="file",
                            device="cdrom",
                            driver=Driver("qemu", "raw"),
                            source=Source(file=cidata_filepath),
                            # backing_store=BackingStore(),
                            target=Target(dev="sda", bus="sata"),
                            readonly=ReadOnly(),
                        ),
                    ],
                    interface=Interface(
                        type="network",
                        source=Source(
                            network="default",
                            bridge='virbr0',
                        ),
                    ),
                    serial=
                        # Serial(
                        #     type="file",
                        #     source=Source(
                        #         path=Path(workspace_path, 'serial.log').as_posix(),
                        #         append='on',
                        #     ),
                        # ),
                        Serial(
                            type="pty",
                            source=Source(path="/dev/pts/0"),
                        ),

                    console=Console(
                        type='pty',
                        source=Source(
                            path='/dev/pts/0',
                        ),
                        target=Target(port='0'),
                    ),
                    graphics=Graphics(
                        type="spice",
                        port="-1",
                        autoport="yes",
                        listen_attribute="127.0.0.1",
                        listen=Listen("address", "127.0.0.1"),
                        image=Image("off"),
                    ),
                    sound=Sound(model="ich9"),
                    audio=Audio(id="1", type="spice"),
                    video=Video(model=Model(type="virtio", heads="1", primary="yes")),
                    memballoon=Memballoon(model="virtio"),
                    rng=Rng(
                        model="virtio",
                        backend=Backend(model="random", value="/dev/urandom"),
                    ),
                    channels=[
                        Channel(
                            type="unix",
                            target=Target(
                                type="virtio",
                                name="org.qemu.guest_agent.0",
                            ),
                        ),
                    ],
                ),
                seclabels=[
                    Seclabel(
                        type="dynamic",
                        model="dac",
                        relabel="yes",
                        label=SeclabelLabel(value="+0:+0")
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

        logging.error("qemu-guest-agent didn't start on time")
        raise libvirt.libvirtError("Qemu Guest Agent didn't start on time")

    def ip(self) -> Optional[str]:
        addresses = self.interfaceAddresses(VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
        for addr in addresses["ens3"]["addrs"]:
            if addr["type"] == 0:  # address type ipv4
                return addr["addr"]

        logging.error("couldn't find machine ip address")
        return None

    def connect_ssh(self) -> paramiko.SSHClient:
        return connect_ssh(
            self.userdata.users[0].name,
            self.ip(),
            gateway_user="root",
            gateway=get_dev_hostname(),
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
                gateway=get_dev_hostname(),
            )
        elif isinstance(src, io.IOBase):
            return upload_file_object(
                src,
                dest,
                self.userdata.users[0].name,
                self.ip(),
                gateway_user="root",
                gateway=get_dev_hostname(),
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
