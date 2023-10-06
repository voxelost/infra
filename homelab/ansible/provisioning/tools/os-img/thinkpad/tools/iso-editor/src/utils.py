import subprocess
import logging
import typing
import uuid
import os
import libvirt


class MultipassException(Exception):
    ...


class Multipass:
    _workdir = "/home/ubuntu/downloads"

    def __init__(self, cpus: int = 4, memory: str = "8G"):
        self._authenticate()

        self._machine_name = f"geniso-{uuid.uuid4()}"
        self._provision_vm(cpus, memory)

        self.cmd(f"mkdir -p {self._workdir}", become=False, cwd=None)

    def __enter__(self):
        return self

    def __exit__(self, reason: typing.Optional[Exception], traceback, *args):
        self._destroy_vm()

    def _provision_vm(self, cpus: int = 4, memory: str = "8G") -> None:
        logging.debug(f"Provisioning VM {self._machine_name}")
        self._shell_cmd(
            f"multipass launch --name {self._machine_name} --cpus {cpus} --memory {memory}"
        )

    def _destroy_vm(self) -> None:
        logging.debug(f"Destroying VM {self._machine_name}")
        self._shell_cmd(f"multipass delete {self._machine_name}")

    def _authenticate(self):
        logging.info(
            "Authenticating multipass. You may need to input the sudo password now"
        )
        self._shell_cmd(f"sudo multipass authenticate {os.getenv('MULTIPASS_AUTH')}")

    def _build_command(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
    ) -> str:
        _cmd = command
        if "|" in _cmd:
            # handle commands with pipe
            _cmd = f"'{_cmd}'"

        if become:
            _cmd = f"sudo {_cmd}"

        _workdir = ""
        if cwd is not None:
            if not cwd.startswith("/"):
                cwd = f"{self._workdir}/{cwd}"

            _workdir = f"--working-directory {cwd}"

        return f"multipass exec {_workdir} {self._machine_name} -- {_cmd}"

    def _shell_cmd(self, cmd: str, stdin: str = "") -> str:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = proc.communicate(stdin)

        if proc.returncode != 0:
            raise MultipassException(stderr)

        return stdout.strip()

    def _send_command(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str = "",
    ) -> str:
        logging.debug(f"Running command: {command}")
        return self._shell_cmd(self._build_command(command, become, cwd), stdin)

    def _transfer(self, src: str, dest: str):
        return self._shell_cmd(f"sudo multipass transfer {src} {dest}")

    def upload(self, src: str, dest: str = "."):
        if not dest.startswith("/"):
            dest = f"{self._workdir}/{dest}"

        logging.debug(f"Uploading file {src} to {dest}")
        return self._transfer(src, f"{self._machine_name}:{dest}")

    def download(self, src: str, dest: str = "."):
        if not src.startswith("/"):
            src = f"{self._workdir}/{src}"

        logging.debug(f"Downloading file {src} to {dest}")
        return self._transfer(f"{self._machine_name}:{src}", dest)

    def cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str = "",
    ) -> str:
        return self._send_command(command, become, cwd, stdin)


class Libvirt:
    def __init__(self):
        con: libvirt.virConnect
        con = libvirt.open()
        hn = con.getHostname()
        print(con, hn)
        # con.getCapabilities()
        stats = con.getInfo()
        print(stats)
