from xml_dataclasses import xml_dataclass, text, dump
from dataclasses import dataclass, field
from typing import Optional
from lxml import etree


@xml_dataclass
@dataclass
class Name:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class Description:
    __ns__ = None

    value: Optional[str] = text(field(default=None))


@xml_dataclass
@dataclass
class DomainSnapshot:
    __ns__ = None

    name: Optional[Name] = field(default=None)
    description: Optional[Description] = field(default=None)

    def to_xml_string(self, indent=False) -> str:
        return etree.tostring(
            dump(self, "domainsnapshot", {}), encoding="unicode", pretty_print=indent
        )
