import paramiko
import logging
import libvirt
import os
import sys
import atexit
from pathlib import Path

from contextlib import contextmanager
from utils.ssh import get_dev_hostname, connect_sftp, get_dev_pem_keyname, get_dev_ssh_connwrapper
from models.libvirt.domain import *

def setup_logging():
    logging.getLogger("paramiko").setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.DEBUG)

def destroy_all_vms(conn: libvirt.virConnect = None):
    if conn is None:
        conn = conn_wrapper()
        atexit.register(conn.close)

    doms = conn.listAllDomains()
    for dom in doms:
        try:
            logging.debug(f"destroying domain {dom.name()}...")
            dom.destroy()
        except Exception as _:
            try:
                logging.debug(f"undefining domain {dom.name()}...")
                dom.undefine()
            except Exception as e:
                print(e)

    with get_dev_ssh_connwrapper() as ssh_client:
        ssh_client.exec_command("cd /root/workspace/; rm ./machines/debby-auto-*")

@contextmanager
def stderr_redirected(to=os.devnull, stderr=None):
    def fileno(file_or_fd):
        fd = getattr(file_or_fd, "fileno", lambda: file_or_fd)()
        if not isinstance(fd, int):
            raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
        return fd

    if stderr is None:
        stderr = sys.stderr

    stderr_fd = fileno(stderr)
    # copy stderr_fd before it is overwritten
    # NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stderr_fd), "wb") as copied:
        stderr.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stderr_fd)
        except ValueError:
            with open(to, "wb") as to_file:
                os.dup2(to_file.fileno(), stderr_fd)  # $ exec > to
        try:
            yield stderr  # allow code to be run with the redirected stderr
        finally:
            # restore stderr to its previous value
            # NOTE: dup2 makes stderr_fd inheritable unconditionally
            stderr.flush()
            os.dup2(copied.fileno(), stderr_fd)  # $ exec >&copied

def get_random_mac_address():
    # TODO: this raised an `libvirt: Domain Config error : XML error: expected unicast mac address, found multicast '5f:9d:70:a6:67:a6'` exception
    # TODO: read on mac address types

    # return ':'.join([hex(random.randint(0, 255))[2:].zfill(2) for _ in range(6)])
    return "00:00:00:{}:{}:{}".format(
        *[hex(random.randint(0, 255))[2:].zfill(2) for _ in range(3)]
    )

DISK_IMAGES = {
    'debian': {
        '11': {
            '_vars': {
                'identifier': '20231004-1523',
                'download_path': 'https://cloud.debian.org/images/cloud/bullseye/{identifier}/{filename}',
                'libos_meta': "http://debian.org/debian/11",
            },
            'generic': {
                'amd64': {
                    'filename': 'debian-11-generic-amd64-{identifier}.qcow2',
                },
            },
            'genericcloud': {
                # https://groups.google.com/g/linux.debian.bugs.dist/c/fpGNuIC7GZc
                # https://salsa.debian.org/kernel-team/linux/-/merge_requests/699
                # https://en.wikipedia.org/wiki/Advanced_Host_Controller_Interface
                'amd64': {
                    'filename': 'debian-11-genericcloud-amd64-{identifier}.qcow2',
                },
            },
            'nocloud': {
                'amd64': {
                    'filename': 'debian-11-nocloud-amd64-{identifier}.qcow2',
                }
            },
        },
        '12': {
            '_vars': {
                'identifier': '20231210-1591',
                'download_path': 'https://cloud.debian.org/images/cloud/bookworm/{identifier}/{filename}',
                'libos_meta': "http://debian.org/debian/11",
            },
            'generic': {
                'amd64': {
                    'filename': 'debian-12-generic-amd64-{identifier}.qcow2',
                },
            },
        },
    },
    'ubuntu': {
        '22.04': {
            '_vars': {
                'download_path': 'https://cloud-images.ubuntu.com/jammy/20231207/{filename}',
                'libos_meta': "http://ubuntu.com/ubuntu/22.04",
            },
            'kvm-optimised': {
                'amd64': {
                    'filename': 'jammy-server-cloudimg-amd64-disk-kvm.img',
                }
            },
        },
    },
}

def get_disk_image_details(os: str, version: str, flavor: str, arch: str) -> dict:
    _image = DISK_IMAGES[os][version][flavor][arch]
    _vars = DISK_IMAGES[os][version]['_vars']
    _image['filename'] = _image['filename'].format(**_vars)
    _vars.update(**_image)
    _vars['download_path'] = _vars['download_path'].format(**_vars)
    return _vars

def ensure_workspace():
    logging.debug('Ensuring workspace directories are present...')
    with get_dev_ssh_connwrapper() as ssh_client:
        ssh_client.exec_command('mkdir -p /root/workspace')
        ssh_client.exec_command('mkdir -p /root/workspace/.cache')
        ssh_client.exec_command('mkdir -p /root/workspace/machines')

def ensure_image_cache():
    logging.debug('Ensuring disk image cache is present on remote host...')
    with get_dev_ssh_connwrapper() as ssh_client:
        cache_path = Path('/root/workspace/.cache').as_posix()
        ssh_client: paramiko.SSHClient
        ssh_client.exec_command(f'mkdir -p {cache_path}')
        with connect_sftp(ssh_client) as sftp_client:
            sftp_client: paramiko.SFTPClient
            sftp_client.put(f'/Users/voxelost/workspace/devops/infra/homelab/vm-manager/{get_dev_pem_keyname()}', '/'.join([cache_path, get_dev_pem_keyname()]))

        for os_name, os_value in DISK_IMAGES.items():
            for version_name, version_value in os_value.items():
                for flavor_name in filter(lambda key: key != '_vars', version_value.keys()):
                    os_variant = version_value[flavor_name]
                    for os_arch_name, os_arch_value in os_variant.items():
                        image = get_disk_image_details(os_name, version_name, flavor_name, os_arch_name)
                        logging.debug(f'Downloading {image["filename"]} if not exists...')
                        _, stdout, _ = ssh_client.exec_command(f'cd {cache_path}; wget -N "{image["download_path"]}"')
                        stdout.read()

def get_default_domain_definition(machine_name: str, memory: int, vcpus: int, source_img_file: str, cidata_filepath: str, libos_meta: str, serial_console: bool = True, workspace_path: Optional[str] = None, metadata: str = '') -> LibvirtDomain:
    if not serial_console and not workspace_path:
        raise Exception('Workspace path must be provided when serial output is set to a logfile')

    _dom = LibvirtDomain(
        type="kvm",
        name=Name(value=machine_name),
        metadata=Metadata(
            libosinfo=Libosinfo(os=Os2(id=libos_meta)),
            # vm_manager=VmManagerMetadata(data=VmManagerMetadataData(data="hello world")),
            vm_manager=VmManagerMetadata(str(metadata)),
        ),
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
        cpu=Cpu(
            mode="host-passthrough",
            check="none",
            migratable="on"),
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
                    target=Target(dev="vda", bus="virtio"),
                ),
                Disk(
                    type="file",
                    device="cdrom",
                    driver=Driver("qemu", "raw"),
                    source=Source(file=cidata_filepath),
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
    )

    if serial_console:
        _dom.devices.serial = Serial(
            type="pty",
            source=Source(path="/dev/pts/0"),
        )
        _dom.devices.console = Console(
            type='pty',
            source=Source(
                path='/dev/pts/0',
            ),
            target=Target(port='0'),
        )
    else:
        _dom.devices.serial = Serial(
            type="file",
            source=Source(
                path=Path(workspace_path, 'serial.log').as_posix(),
                append='on',
            ),
        )

    return _dom
