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
from utils.dump import stderr_redirected, get_disk_image_details, get_default_domain_definition, get_dev_ssh_connwrapper
from utils.ssh import connect_ssh, connect_sftp, upload_file_path, upload_file_object, get_dev_pkey, get_dev_pem_keyname, get_dev_hostname, get_dev_proxies
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

        self.userdata: UserData = userdata
        self.metadata: MetaData = metadata

        try:
            self._wait_for_qemu_ga()
        except Exception as e:
            logging.error(e)

        res = self.exec_ssh_cmd("cloud-init status --wait")
        logging.debug(f"cloud init status: {res}")

    def __getattr__(self, name: str):
        return getattr(self._proxied, name)

    @classmethod
    def create_default(
        cls, conn: libvirt.virConnect, memory: int = 2097152, vcpus: int = 4, disk_size: int = 10,
    ):
        machine_uuid = str(uuid.uuid1()).split('-')[0]
        machine_name =  machine_uuid
        workspace_path = Path('/root/workspace/machines', machine_uuid).as_posix()
        source_img_file = Path(workspace_path, f"{machine_name}.qcow2").as_posix()
        cidata_filepath = Path(workspace_path, "cidata.iso").as_posix()

        userdata = UserData.create_default()
        metadata = MetaData(machine_name, machine_name)

        logging.debug(f'machine uuid: {machine_uuid}')

        with get_dev_ssh_connwrapper() as ssh_client:
            ssh_client.exec_command(
                f"mkdir -p /root/workspace/machines {workspace_path}"
            )

            chosen_img = get_disk_image_details('debian', '12', 'generic', 'amd64')
            # chosen_img = get_disk_image_details('ubuntu', '22.04', 'kvm-optimised', 'amd64')
            DEBIAN_QCOW_FILENAME = chosen_img['filename']
            LIBOS_META = chosen_img['libos_meta']

            ssh_client.exec_command(
                f"cp /root/workspace/.cache/{DEBIAN_QCOW_FILENAME} {source_img_file}"
            )

            ssh_client.exec_command(
                f"cp /root/workspace/.cache/{get_dev_pem_keyname()} {workspace_path}"
            )

            ssh_client.exec_command(
                f"chmod 400 {workspace_path}/{get_dev_pem_keyname()}"
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

                stfp_client.putfo(ci_data.file_object, cidata_filepath)

            logging.debug(f'Extending {source_img_file} to 10G...')
            _, stdout, _ = ssh_client.exec_command(f'qemu-img resize {source_img_file} 10G')
            logging.debug(stdout.read())

        _vd = conn.createXML(
            get_default_domain_definition(machine_name,
                memory,
                vcpus,
                source_img_file,
                cidata_filepath,
                LIBOS_META,
                serial_console=False,
                workspace_path=workspace_path,
                metadata=json.dumps(debug_data),
            ).to_xml_string()
        )

        return cls(_vd, userdata, metadata)

    def _wait_for_qemu_ga(self, tries: int = 50, delay: Optional[int] = None):
        # TODO: consider using this as a decorator like `ensure_ga`

        _dynamic_delay = not delay
        if _dynamic_delay:
            delay = 5

        for i in range(tries):
            try:
                with stderr_redirected():
                    self.hostname(libvirt.VIR_DOMAIN_GET_HOSTNAME_AGENT)
                return
            except Exception as e:
                if "err" in dir(e) and e.err[0] != libvirt.VIR_ERR_AGENT_UNRESPONSIVE:
                    raise e

                logging.debug(
                    f"[{i+1}/{tries}] waiting {delay}s for qemu-guest-agent to start..."
                )

                time.sleep(delay)
                if _dynamic_delay:
                    delay += 5

        raise libvirt.libvirtError("Qemu Guest Agent didn't start on time")

    def ip(self) -> Optional[str]:
        # when using proxied connections, this sometimes panics with "libvirt: XML-RPC error : internal error: client socket is closed"
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
            *get_dev_proxies("root", get_dev_hostname()),
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
            )
        elif isinstance(src, io.IOBase):
            return upload_file_object(
                src,
                dest,
                self.userdata.users[0].name,
                self.ip(),
            )
        else:
            raise Exception(f"Wrong argument type: {type(src)}")

    def download_file(self, src: str, dest: str):
        with self.connect_ssh() as ssh_client:
            with connect_sftp(ssh_client) as sftp_client:
                def progress(sent: int, total: int):
                    logging.debug(f"[{sent}/{total}] Downloading file {src}")

                sftp_client.get(
                    src, dest, callback=progress
                )  # TODO: handle dest directories

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
