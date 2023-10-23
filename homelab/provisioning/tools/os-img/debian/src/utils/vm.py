import typing
from abc import abstractmethod


class VM:
    @property
    @abstractmethod
    def _workdir(self):
        ...

    @abstractmethod
    def _provision_vm(self, *args, **kwargs):
        ...

    @abstractmethod
    def _destroy_vm(self, *args, **kwargs):
        ...

    @abstractmethod
    def upload(self, src: str, dest: str = ".") -> str:
        ...

    @abstractmethod
    def download(self, src: str, dest: str = ".") -> str:
        ...

    @abstractmethod
    def cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str = "",
        pipe: bool = True,
    ) -> str:
        ...
