import paramiko
import logging
from contextlib import contextmanager
from typing import IO, Optional
from os import PathLike
from pathlib import Path

def get_dev_host() -> str:
    return "thinkpad"

def get_dev_pem_keyname() -> str:
    return f"{get_dev_host()}.pem"

def get_dev_hostname() -> str:
    return f"{get_dev_host()}.local"

def get_nuc_pkey(
    filepath: PathLike = f"/Users/voxelost/workspace/devops/infra/homelab/vm-manager/{get_dev_pem_keyname()}",
) -> paramiko.PKey:
    return paramiko.PKey.from_path(filepath)

@contextmanager
def connect_ssh(
    user: str,
    host: str,
    pkey: paramiko.PKey = get_nuc_pkey(),
    gateway_user: Optional[str] = None,
    gateway: Optional[str] = None,
) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy)
    sock = None
    if gateway:
        if gateway_user is None:
            gateway_user = user

        gw_client = connect_ssh(gateway_user, gateway, pkey).gen.__next__()
        sock = gw_client.get_transport().open_channel(
            "direct-tcpip", (host, 22), ("", 0)
        )

    client.connect(
        host,
        port=22,
        username=user,
        pkey=pkey,
        sock=sock,
    )

    yield client
    return client.close()


@contextmanager
def connect_sftp(ssh_client: paramiko.SSHClient) -> paramiko.SFTPClient:
    stfp_client = ssh_client.open_sftp()
    if stfp_client is None:
        raise paramiko.SSHException("Couldn't create an SFTP client")

    yield stfp_client
    return stfp_client.close()


def upload_file_path(
    src: PathLike,
    dest: PathLike,
    user: str,
    host: str,
    pkey: paramiko.PKey = get_nuc_pkey(),
    gateway_user: Optional[str] = None,
    gateway: Optional[str] = None,
):
    with open(src, "rb") as fptr:
        return upload_file_object(fptr, dest, user, host, pkey, gateway_user, gateway)


def upload_file_object(
    fo: IO[bytes],
    dest: PathLike,
    user: str,
    host: str,
    pkey: paramiko.PKey = get_nuc_pkey(),
    gateway_user: Optional[str] = None,
    gateway: Optional[str] = None,
):
    if isinstance(dest, Path):
        dest = dest.as_posix()

    with connect_ssh(
        user, host, pkey, gateway_user=gateway_user, gateway=gateway
    ) as ssh_client:
        with connect_sftp(ssh_client) as stfp_client:

            def _progress(sent: int, total: int):
                logging.debug(f"[{sent}/{total}] Uploading file...")

            stfp_client.putfo(
                fo, dest, callback=_progress
            )  # TODO: handle dest directories
