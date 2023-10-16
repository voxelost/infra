import subprocess
import logging
import typing
import uuid
import os
import shutil
import tempfile
import yaml
from jinja2 import Environment, FileSystemLoader
from functools import cached_property


class MultipassException(Exception):
    ...


class Multipass:
    _workdir = "/home/ubuntu/downloads"
    _templates_path = "templates"

    def __init__(
        self, flash_target_config_file: str, cpus: int = 4, memory: str = "8G"
    ):
        self._authenticate()

        self.flash_target_config_file = flash_target_config_file
        self._machine_name = f"geniso-{uuid.uuid4()}"
        self._provision_vm(cpus, memory)

        self.cmd(f"mkdir -p {self._workdir}", become=False, cwd=None)

    def __enter__(self):
        _ = self._tempdir  # ensure temp dir is created
        return self

    def __exit__(self, reason: typing.Optional[Exception], traceback, *args):
        if os.path.isdir(self._tempdir):
            logging.debug(f"Removing temporary directory {self._tempdir}")
            shutil.rmtree(self._tempdir)

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
        _auth = os.getenv("MULTIPASS_AUTH")
        if _auth is None:
            logging.error(
                "Env var MULTIPASS_AUTH needs to be set to authenticate multipass"
            )

        logging.info(
            "Authenticating multipass. You may need to input the sudo password now"
        )
        self._shell_cmd(
            f"sudo multipass authenticate {_auth}",
        )

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

    def _transfer(self, src: str, dest: str) -> str:
        return self._shell_cmd(f"sudo multipass transfer {src} {dest}")

    @cached_property
    def _jinja_env(self) -> Environment:
        jinja_loader = FileSystemLoader(Multipass._templates_path)
        return Environment(loader=jinja_loader)

    @cached_property
    def _tempdir(self) -> str:
        tempdir = tempfile.mkdtemp()
        logging.debug(f"Created temporary directory {tempdir}")
        return tempdir

    @cached_property
    def _preseed_config(self) -> dict:
        with open(self.flash_target_config_file, "r") as fptr:
            return yaml.safe_load(fptr)

    def upload(self, src: str, dest: str = ".") -> str:
        if not dest.startswith("/"):
            dest = f"{self._workdir}/{dest}"

        logging.debug(f"Uploading file {os.path.basename(src)}")
        return self._transfer(src, f"{self._machine_name}:{dest}")

    def download(self, src: str, dest: str = ".") -> str:
        if not src.startswith("/"):
            src = f"{self._workdir}/{src}"

        _dest = os.path.abspath(dest)
        logging.debug(f"Ensuring {_dest} exists")
        os.makedirs(os.path.abspath(dest), exist_ok=True)

        logging.debug(f"Downloading file {os.path.basename(src)}")
        return self._transfer(f"{self._machine_name}:{src}", _dest)

    def upload_rendered_template(
        self, template_name: str, dest_fname: str = None
    ) -> str:
        if dest_fname is None:
            dest_fname = template_name.removesuffix(".j2").removesuffix(".jinja2")

        preseed_rendered_fname = os.path.join(self._tempdir, dest_fname)
        with open(preseed_rendered_fname, "w") as fptr:
            _template = self._jinja_env.get_template(template_name)
            fptr.write(_template.render(self._preseed_config))

        return self.upload(preseed_rendered_fname, dest_fname)

    def cmd(
        self,
        command: str,
        become: bool = True,
        cwd: typing.Optional[str] = _workdir,
        stdin: str = "",
    ) -> str:
        return self._send_command(command, become, cwd, stdin)
