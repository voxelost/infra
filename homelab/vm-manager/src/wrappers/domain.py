import time
import logging
import paramiko
import uuid
import io
import json
import libvirt
import datetime
from libvirt import virDomain, VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT
from typing import Optional, Dict, IO, Union
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from functools import singledispatch
from utils.dump import stderr_redirected
from utils.ssh import connect_ssh, connect_sftp, upload_file_path, upload_file_object
from utils.default_helpers.default_debian import get_default_machine
from utils.default_helpers.default_userdata import get_default_userdata
from models.cloud_init.userdata import UserData
from models.cloud_init.metadata import MetaData
from models.libvirt.snapshot import DomainSnapshot, Name, Description

class Domain(virDomain):
    def __init__(self, vd: virDomain, userdata: Optional[UserData], metadata: Optional[MetaData]):
        self._proxied = vd
        self._wait_for_qemu_ga()

        self.userdata: UserData = userdata
        self.metadata: MetaData = metadata

    def __getattr__(self, name: str):
        return getattr(self._proxied, name)

    @classmethod
    def create_default(cls, conn: libvirt.virConnect):
        machine_name = f'debby-auto-{uuid.uuid4()!s}'
        source_img_file = f'/root/workspace/{machine_name}.qcow2'
        cidata_filepath = '/root/workspace/cidata.iso'

        with connect_ssh('root', 'nuc.local') as ssh_client:
            ssh_client.exec_command(f'cp /root/workspace/.cache/debby-generic-11.qcow2 {source_img_file}')

            userdata = get_default_userdata()
            metadata = MetaData(machine_name, machine_name[:15])

            with connect_sftp(ssh_client) as stfp_client:
                with io.StringIO(userdata.to_yaml()) as fl:
                    stfp_client.putfo(fl, '/root/workspace/user-data')

                with io.StringIO(metadata.to_yaml()) as fl:
                    stfp_client.putfo(fl, '/root/workspace/meta-data')

            ssh_client.exec_command('cd /root/workspace/; genisoimage -output cidata.iso -V cidata -r -J user-data meta-data')

        _vd = conn.createXML(get_default_machine(machine_name, source_img_file, cidata_filepath).to_xml_string())
        return cls(_vd, userdata, metadata)

    def _wait_for_qemu_ga(self, tries=50):
        # TODO: consider using this as a decorator like `ensure_ga`

        for i in range(tries):
            try:
                with stderr_redirected():
                    self.hostname(libvirt.VIR_DOMAIN_GET_HOSTNAME_AGENT)
                return
            except Exception as e:
                if 'err' in dir(e) and e.err[0] != libvirt.VIR_ERR_AGENT_UNRESPONSIVE:
                    raise e

                logging.debug(f'[{i+1}/{tries}] waiting for qemu-guest-agent to start...')
                time.sleep(5)

        logging.error("qemu-user-agent didn't start on time")
        raise libvirt.libvirtError("Qemu Guest Agent didn't start on time")

    def ip(self) -> Optional[str]:
        addresses = self.interfaceAddresses(VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
        for addr in addresses['enp1s0']['addrs']:
            if addr['type'] == 0: # address type ipv4
                return addr['addr']

        logging.error("couldn't find machine ip address")
        return None

    def connect_ssh(self) -> paramiko.SSHClient:
        return connect_ssh(
            self.userdata.users[0].name,
            self.ip(),
            gateway_user='root',
            gateway='nuc.local',
        )

    def exec_ssh_cmd(self, cmd: str, env: Optional[Dict[str, str]] = None, ignore_error: bool = False) -> str:
        with self.connect_ssh() as ssh_client:
            _, stdout, stderr = ssh_client.exec_command(cmd, environment=env)
            _stderr = stderr.read().strip()
            if len(_stderr) > 0 and not ignore_error:
                raise paramiko.SSHException(str(_stderr, 'utf-8'))

            return str(stdout.read(), 'utf-8').strip()

    def upload_file(self, src: Union[str, IO], dest: str):
        if isinstance(src, str):
            return upload_file_path(src, dest, self.userdata.users[0].name, self.ip(), gateway_user='root', gateway='nuc.local')
        elif isinstance(src, io.IOBase):
            return upload_file_object(src, dest, self.userdata.users[0].name, self.ip(), gateway_user='root', gateway='nuc.local')
        else:
            raise Exception(f'Wrong argument type: {type(src)}')

    def download_file(self, src: str, dest: str):
        with self.connect_ssh() as ssh_client:
            stfp_client = ssh_client.open_sftp()
            if stfp_client is None:
                raise paramiko.SSHException("Couldn't create an SFTP client")

            def progress(sent: int, total: int):
                logging.debug(f'[{sent}/{total}] Downloading file {src}')

            stfp_client.get(src, dest, callback=progress) # TODO: handle dest directories
            stfp_client.close()

    def create_snapshot(self) -> libvirt.virDomainSnapshot:
        _uuid = str(uuid.uuid4())
        return self.snapshotCreateXML(DomainSnapshot(
            name=Name(_uuid),
            description=Description(json.dumps({
                'date': str(datetime.datetime.now()),
                'name': _uuid,
            })),
        ).to_xml_string(), libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC)
