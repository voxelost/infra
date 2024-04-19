import libvirt
from contextlib import contextmanager
from utils.ssh import get_dev_host, get_dev_pem_keyname, get_dev_hostname
from pathlib import Path

@contextmanager
def conn_wrapper():
    protocols = ['qemu', 'ssh']
    remote_user = 'root'
    remote_address = get_dev_hostname()
    url_params = {
        'no_verify': 1,
        # 'keyfile': Path('/Users/voxelost/workspace/devops/infra/homelab/provisioning/', get_dev_host(), get_dev_pem_keyname()).as_posix(),
        # 'sshauth': 'privkey',
    }
    _protocols_str = '+'.join(protocols)
    _params_str = '&'.join(f'{k}={v}' for k, v in url_params.items())

    QEMU_CONN_STR = f"{_protocols_str}://{remote_user}@{remote_address}/system?{_params_str}"
    conn: libvirt.virConnect = libvirt.open(QEMU_CONN_STR)
    if not conn:
        raise SystemExit(f"Failed to open connection to {QEMU_CONN_STR}")

    yield conn

    print('closing connection...')
    return conn.close()
