import libvirt
from contextlib import contextmanager
from utils.ssh import get_dev_host, get_dev_pem_keyname, get_dev_hostname

@contextmanager
def conn_wrapper():
    QEMU_CONN_STR = f"qemu+ssh://root@{get_dev_hostname()}/system?no_verify=1&keyfile=/Users/voxelost/workspace/devops/infra/homelab/provisioning/{get_dev_host()}/{get_dev_pem_keyname()}&sshauth=privkey"
    conn: libvirt.virConnect = libvirt.open(QEMU_CONN_STR)
    if not conn:
        raise SystemExit(f"Failed to open connection to {QEMU_CONN_STR}")

    yield conn

    print('closing connection...')
    return conn.close()
