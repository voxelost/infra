import paramiko
import uuid
import random
import io
from utils.default_helpers.default_userdata import get_default_userdata
from models.cloud_init.metadata import MetaData
from models.libvirt.domain import *


def setup_remote_files(machine_name: str, source_img_file: str):
    _IMAGE_FLAVOR = 'generic'

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy)
    ssh_client.connect('nuc.local', username='root', pkey=paramiko.PKey.from_path('/Users/voxelost/workspace/devops/infra/homelab/vm-manager/nuc.pem'))
    ssh_client.exec_command(f'cp /root/workspace/.cache/debby-{_IMAGE_FLAVOR}-11.qcow2 {source_img_file}')

    sftp_client = ssh_client.open_sftp()

    with io.StringIO(get_default_userdata().to_yaml()) as fl:
        sftp_client.putfo(fl, '/root/workspace/user-data')

    with io.StringIO(MetaData(machine_name, machine_name[:15]).to_yaml()) as fl:
        sftp_client.putfo(fl, '/root/workspace/meta-data')

    sftp_client.close()
    ssh_client.exec_command('cd /root/workspace/; genisoimage -output cidata.iso -V cidata -r -J user-data meta-data')

def get_random_mac_address():
    seed = random.randint(0, 16**6)
    hex_num = hex(seed)[2:].zfill(6)
    return "00:00:00:{}{}:{}{}:{}{}".format(*hex_num)


def get_default_machine(memory: int = 2097152) -> Domain:
    # TODO: graphics_port should be assigned dynamically
    machine_name = f'debby-auto-{uuid.uuid4()!s}'
    source_img_file = f'/root/workspace/{machine_name}.qcow2'
    cidata_filepath = '/root/workspace/cidata.iso' # TODO

    setup_remote_files(machine_name, source_img_file)

    return Domain(
        'kvm',
        '1',
        DomainName(machine_name),
        Metadata(
            Libosinfo(
                Os2('http://debian.org/debian/11')
            )
        ),
        Memory('KiB', str(memory)),
        Vcpu('static', '2'),
        Resource(ResourcePartition('/machine')),
        Os1(TypeType('x86_64', 'pc-q35-7.2', 'hvm'), Boot('hd')),
        Features(Acpi(), Apic(), Vmport('off')),
        Cpu('host-passthrough', 'none', 'on'),
        Clock('utc', [
            Timer('rtc', tickpolicy='catchup'),
            Timer('pit', tickpolicy='delay'),
            Timer('hpet', present='no'),
        ]),
        OnPoweroff('destroy'),
        OnReboot('restart'),
        OnCrash('destroy'),
        Pm(
            SuspendToMem('no'),
            SuspendToDisk('no')
        ),
        Devices(
            Emulator('/usr/bin/qemu-system-x86_64'),
            [
                Disk(
                    type_value='file',
                    device='disk',
                    driver=Driver('qemu', 'qcow2'),
                    source=Source(file=source_img_file, index='2'),
                    backing_store=BackingStore(),
                    target=Target(dev='vda', bus='virtio'),
                    alias=Alias('virtio-disk0'),
                    address=Address(type_value='pci', domain='0x0000', bus='0x04', slot='0x00', function='0x0'),
                ),
                Disk(
                    type_value='file',
                    device='cdrom',
                    driver=Driver('qemu', 'raw'),
                    source=Source(file=cidata_filepath, index='1'),
                    backing_store=BackingStore(),
                    target=Target(dev='sda', bus='sata'),
                    readonly=ReadOnly(),
                    alias=Alias('sata0-0-0'),
                    address=Address(type_value='drive', controller='0', bus='0', target='0', unit='0'),
                )
            ],
            Interface(
                'network',
                Mac(get_random_mac_address()),
                Source(
                    'default',
                    'bbbd2004-3294-4ecd-a1cc-f43d4f3c26a0', # should this be unique?
                    'virbr0',
                ),
                Target(dev='vnet0'),
                Model('virtio'),
                Alias('net0'),
                Address('pci', '0x0000', '0x01', '0x00', '0x0'),
            ),
            Serial(
                'pty',
                Source(path='/dev/pts/2'),
                Target('isa-serial', '0', Model(name='isa-serial')),
                Alias('serial0'),
            ),
            Console(
                'pty',
                '/dev/pty/2',
                Source(path='/dev/pts/2'),
                Target('serial', '0'),
                Alias('serial0'),
            ),
            Graphics(
                'spice',
                '5900',
                'yes',
                '127.0.0.1',
                Listen('address', '127.0.0.1'),
                Image('off'),
            ),
            Sound(
                'ich9',
                Alias('sound0'),
                Address('pci', '0x0000', '0x00', '0x1b', '0x0'),
            ),
            Audio('1', 'spice'),
            Video(
                Model('virtio', '1', 'yes'),
                Alias('video0'),
                Address('pci', '0x0000', '0x00', '0x01', '0x0')
            ),
            Memballoon(
                'virtio',
                Alias('balloon0'),
                Address('pci', '0x0000', '0x05', '0x00', '0x0'),
            ),
            Rng(
                'virtio',
                Backend('random', '/dev/urandom'),
                Alias('rng0'),
                Address('pci', '0x0000', '0x06', '0x00', '0x0'),
            ),
            Channel(
                type_value='unix',
                target=Target(
                    type_value='virtio',
                    name='org.qemu.guest_agent.0',
                ),
            ),
        ),
        [
            Seclabel('dynamic', 'apparmor', 'yes'),
            Seclabel('dynamic', 'dac', 'yes', SeclabelLabel('+0:+0'), SeclabelImageLabel('+0:+0')),
        ]
    )
