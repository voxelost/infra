from abc import ABC, abstractmethod

from src.models.infra.host import Host
from wrappers.domain import Domain


class Migration(ABC):
    def __init__(self, domain: Domain, destination: Host):
        self.domain = domain
        self.destination = destination
        domain.migrate

    # def __init_subclass__(cls):
    #     ...

    @abstractmethod
    def begin(self):
        ...
