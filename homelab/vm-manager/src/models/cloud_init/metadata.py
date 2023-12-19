from dataclasses import dataclass, field, asdict
from models.cloud_init.cloud_init import CloudInitObj
import yaml


@dataclass
class MetaData(CloudInitObj):
    _FILENAME = 'meta-data'

    instance_id: str = field(default="debby")
    local_hostname: str = field(default="debby")

    @classmethod
    def create_default(cls):
        return cls()

    def to_yaml(self) -> str:
        return yaml.safe_dump({
            'instance-id': self.instance_id,
            'local-hostname': self.local_hostname
        })
