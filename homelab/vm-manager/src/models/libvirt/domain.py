from dataclasses import field, dataclass
from xml_dataclasses import xml_dataclass, rename, text, dump, load, XmlDataclass
from lxml import etree
from typing import List, Optional, Union, IO
from os import PathLike

LIBOS_METADATA_NS = "http://libosinfo.org/xmlns/libvirt/domain/1.0"


@xml_dataclass
@dataclass
class Address:
    __ns__ = None

    type: Optional[str] = field(default=None)
    domain: Optional[str] = field(default=None)
    bus: Optional[str] = field(default=None)
    slot: Optional[str] = field(default=None)
    function: Optional[str] = field(default=None)
    controller: Optional[str] = field(default=None)
    target: Optional[str] = field(default=None)
    unit: Optional[str] = field(default=None)
    port: Optional[str] = field(default=None)
    multifunction: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Alias:
    __ns__ = None

    name: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Audio:
    __ns__ = None

    id: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Backend:
    __ns__ = None

    model: Optional[str] = field(default=None)
    value: str = text(field(default="/dev/urandom"))


@xml_dataclass
@dataclass
class Boot:
    __ns__ = None

    dev: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Cpu:
    __ns__ = None

    mode: Optional[str] = field(default=None)
    check: Optional[str] = field(default=None)
    migratable: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Driver:
    __ns__ = None

    name: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Image:
    __ns__ = None

    compression: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Listen:
    __ns__ = None

    type: Optional[str] = field(default=None)
    address: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Mac:
    __ns__ = None

    address: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Memory:
    __ns__ = None

    unit: Optional[str] = field(default=None)
    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Uuid:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Model:
    __ns__ = None

    type: Optional[str] = field(default=None)
    heads: Optional[str] = field(default=None)
    primary: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class ResourcePartition:
    __ns__ = None

    partition: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Resource:
    __ns__ = None

    partition: Optional[ResourcePartition] = field(default=None)


@xml_dataclass
@dataclass
class SeclabelLabel:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class SeclabelImageLabel:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Seclabel:
    __ns__ = None

    type: Optional[str] = field(default=None)
    model: Optional[str] = field(default=None)
    relabel: Optional[str] = field(default=None)
    label: Optional[SeclabelLabel] = field(default=None)
    imagelabel: Optional[SeclabelImageLabel] = field(default=None)


@xml_dataclass
@dataclass
class Source:
    __ns__ = None

    network: Optional[str] = field(default=None)
    portid: Optional[str] = field(default=None)
    bridge: Optional[str] = field(default=None)
    file: Optional[str] = field(default=None)
    index: Optional[str] = field(default=None)
    path: Optional[str] = field(default=None)
    mode: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class SuspendToDisk:
    __ns__ = None

    enabled: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class SuspendToMem:
    __ns__ = None

    enabled: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Timer:
    __ns__ = None

    name: Optional[str] = field(default=None)
    present: Optional[str] = field(default=None)
    tickpolicy: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class TypeType:
    __ns__ = None

    arch: Optional[str] = field(default=None)
    machine: Optional[str] = field(default=None)
    value: str = text(
        field(
            default="",
        )
    )


@xml_dataclass
@dataclass
class Vcpu:
    __ns__ = None

    placement: Optional[str] = field(default=None)
    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Vmport:
    __ns__ = None

    state: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Os2:
    __ns__ = LIBOS_METADATA_NS

    id: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Clock:
    __ns__ = None

    offset: Optional[str] = field(default=None)
    timers: List[Timer] = rename(field(default_factory=list), name="timer")


@xml_dataclass
@dataclass
class Acpi:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Apic:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Features:
    __ns__ = None

    acpi: Optional[Acpi] = field(default=None)
    apic: Optional[Apic] = field(default=None)
    vmport: Optional[Vmport] = field(default=None)


@xml_dataclass
@dataclass
class Graphics:
    __ns__ = None

    type: Optional[str] = field(default=None)
    port: Optional[str] = field(default=None)
    autoport: Optional[str] = field(default=None)
    listen_attribute: Optional[str] = rename(field(default=None), name="listen")
    listen: Optional[Listen] = field(default=None)
    image: Optional[Image] = field(default=None)


@xml_dataclass
@dataclass
class Memballoon:
    __ns__ = None

    model: Optional[str] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Os1:
    __ns__ = None

    type: Optional[TypeType] = field(default=None)
    boot: Optional[Boot] = field(default=None)


@xml_dataclass
@dataclass
class PowerManagement:
    __ns__ = None

    suspend_to_mem: Optional[SuspendToMem] = rename(
        field(default=None), name="suspend-to-mem"
    )
    suspend_to_disk: Optional[SuspendToDisk] = rename(
        field(default=None), name="suspend-to-disk"
    )


@xml_dataclass
@dataclass
class Rng:
    __ns__ = None

    model: Optional[str] = field(default=None)
    backend: Optional[Backend] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Sound:
    __ns__ = None

    model: Optional[str] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Target:
    __ns__ = None

    type: Optional[str] = field(default=None)
    port: Optional[str] = field(default=None)
    model: Optional[Model] = field(default=None)
    dev: Optional[str] = field(default=None)
    bus: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    state: Optional[str] = field(default=None)
    chassis: Optional[str] = field(default=None)


@xml_dataclass
@dataclass
class Video:
    __ns__ = None

    model: Optional[Model] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Libosinfo:
    __ns__ = LIBOS_METADATA_NS
    __nsmap__ = {"libosinfo": LIBOS_METADATA_NS}

    os: Optional[Os2] = field(default=None)


@xml_dataclass
@dataclass
class VmManagerMetadata:
    __ns__ = "https://internal.local"
    __nsmap__ = {
        "internal": "https://internal.local",
    }

    data: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Console:
    __ns__ = None

    type: Optional[str] = field(default=None)
    tty: Optional[str] = field(default=None)
    source: Optional[Source] = field(default=None)
    target: Optional[Target] = field(default=None)
    alias: Optional[Alias] = field(default=None)


@xml_dataclass
@dataclass
class BackingStore:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class ReadOnly:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Disk:
    __ns__ = None

    type: Optional[str] = field(default=None)
    device: Optional[str] = field(default=None)
    driver: Optional[Driver] = field(default=None)
    source: Optional[Source] = field(default=None)
    backing_store: Optional[BackingStore] = rename(
        field(default=None), name="backingStore"
    )
    readonly: Optional[ReadOnly] = field(default=None)
    target: Optional[Target] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Interface:
    __ns__ = None

    type: Optional[str] = field(default=None)
    mac: Optional[Mac] = field(default=None)
    source: Optional[Source] = field(default=None)
    target: Optional[Target] = field(default=None)
    model: Optional[Model] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)


@xml_dataclass
@dataclass
class Metadata:
    __ns__ = None

    libosinfo: Optional[Libosinfo] = field(default=None)
    vm_manager: Optional[VmManagerMetadata] = field(default=None)


@xml_dataclass
@dataclass
class Serial:
    __ns__ = None

    type: Optional[str] = field(default=None)
    source: Optional[Source] = field(default=None)
    target: Optional[Target] = field(default=None)
    alias: Optional[Alias] = field(default=None)


@xml_dataclass
@dataclass
class Emulator:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Channel:
    __ns__ = None

    type: Optional[str] = field(default=None)
    target: Optional[Target] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)
    source: Optional[Source] = field(default=None)


@xml_dataclass
@dataclass
class Controller:
    __ns__ = None

    type: Optional[str] = field(default=None)
    index: Optional[str] = field(default=None)
    model: Optional[str] = field(default=None)
    alias: Optional[Alias] = field(default=None)
    address: Optional[Address] = field(default=None)
    model_attribute: Optional[str] = rename(field(default=None), name="model")
    model: Optional[Model] = field(default=None)
    target: Optional[Target] = field(default=None)


@xml_dataclass
@dataclass
class Input:
    __ns__ = None

    type: Optional[str] = field(default=None)
    bus: Optional[str] = field(default=None)
    alias: Optional[Alias] = field(default=None)


@xml_dataclass
@dataclass
class Devices:
    __ns__ = None

    emulator: Optional[Emulator] = field(default=None)
    disks: List[Disk] = rename(field(default_factory=list), name="disk")
    interface: Optional[Interface] = field(default=None)
    serial: Optional[Serial] = field(default=None)
    console: Optional[Console] = field(default=None)
    graphics: Optional[Graphics] = field(default=None)
    sound: Optional[Sound] = field(default=None)
    audio: Optional[Audio] = field(default=None)
    video: Optional[Video] = field(default=None)
    memballoon: Optional[Memballoon] = field(default=None)
    rng: Optional[Rng] = field(default=None)
    channel: Optional[Channel] = field(default=None)
    inputs: List[Input] = rename(field(default_factory=list), name="input")
    controllers: List[Controller] = rename(
        field(default_factory=list), name="controller"
    )


@xml_dataclass
@dataclass
class OnPoweroff:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class OnReboot:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class OnCrash:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class DomainName:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class LibvirtDomain(XmlDataclass):
    __ns__ = None

    type: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
    name: Optional[DomainName] = field(default=None)
    max_memory: Optional[Memory] = rename(field(default=None), name='maxMemory')
    metadata: Optional[Metadata] = field(default=None)
    current_memory: Optional[Memory] = rename(field(default=None), name='currentMemory')
    memory: Optional[Memory] = field(default=None)
    vcpu: Optional[Vcpu] = field(default=None)
    resource: Optional[Resource] = field(default=None)
    os: Optional[Os1] = field(default=None)
    features: Optional[Features] = field(default=None)
    cpu: Optional[Cpu] = field(default=None)
    clock: Optional[Clock] = field(default=None)
    on_poweroff: Optional[OnPoweroff] = field(default=None)
    on_reboot: Optional[OnReboot] = field(default=None)
    on_crash: Optional[OnCrash] = field(default=None)
    power_management: Optional[PowerManagement] = rename(field(default=None), name='pm')
    devices: Optional[Devices] = field(default=None)
    seclabels: List[Seclabel] = rename(field(default_factory=list), name="seclabel")
    uuid: Optional[Uuid] = field(default=None)
    current_memory: Optional[Memory] = rename(field(default=None), name="currentMemory")

    @classmethod
    def from_xml_string(cls, source: str):
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        lxml_el_in = etree.fromstring(source, parser).getroot()
        return load(LibvirtDomain, lxml_el_in, "domain")

    @classmethod
    def from_xml_file(cls, source: Union[PathLike, IO]):
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        lxml_el_in = etree.parse(source, parser).getroot()
        return load(LibvirtDomain, lxml_el_in, "domain")

    def to_xml_string(self, indent=False) -> str:
        return etree.tostring(
            dump(self, "domain", {}), encoding="unicode", pretty_print=indent
        )
