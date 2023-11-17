from abc import ABC, abstractproperty, abstractmethod

class CloudInitObj(ABC):
    @property
    @abstractmethod
    def _FILENAME(self) -> str: ...

    @abstractmethod
    def to_yaml(self) -> str: ...
