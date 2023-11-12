import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class MetaData:
    instance_id: str = field(default='debby', metadata={'attr_name': 'instance-id'})
    local_hostname: str = field(default='debby', metadata={'attr_name': 'local-hostname'})

    def to_yaml(self) -> str:
        return yaml.safe_dump(asdict(self))
