import libvirt
from contextlib import contextmanager


# @contextmanager
def conn_wrapper():
    QEMU_CONN_STR = "qemu+ssh://root@nuc.local/system?no_verify=1&keyfile=/Users/voxelost/workspace/devops/infra/homelab/provisioning/nuc/nuc.pem&sshauth=privkey"
    conn: libvirt.virConnect = libvirt.open(QEMU_CONN_STR)
    if not conn:
        raise SystemExit(f"Failed to open connection to {QEMU_CONN_STR}")

    return conn

    # print('closing connection...')
    # return conn.close()
