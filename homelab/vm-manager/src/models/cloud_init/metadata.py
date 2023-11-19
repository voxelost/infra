from dataclasses import dataclass, field, asdict
from models.cloud_init.cloud_init import CloudInitObj
import yaml


@dataclass
class MetaData(CloudInitObj):
    _FILENAME = 'meta-data'

    instance_id: str = field(default="debby", metadata={"attr_name": "instance-id"})
    local_hostname: str = field(
        default="debby", metadata={"attr_name": "local-hostname"}
    )

    @classmethod
    def create_default(cls):
        return cls()

    def to_yaml(self) -> str:
        return yaml.safe_dump(asdict(self))
