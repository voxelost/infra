import paramiko
import logging
import libvirt
import os
import sys

from contextlib import contextmanager
from utils.ssh import connect_ssh


def setup_logging():
    logging.getLogger("paramiko").setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.DEBUG)


def destroy_all_vms(conn: libvirt.virConnect = None):
    if conn is None:
        conn = conn_wrapper()
        import atexit

        atexit.register(conn.close)
    doms = conn.listAllDomains()
    for dom in doms:
        try:
            logging.debug(f"destroying domain {dom.name()}...")
            dom.destroy()
        except Exception as _:
            try:
                logging.debug(f"undefining domain {dom.name()}...")
                dom.undefine()
            except Exception as e:
                print(e)

    with connect_ssh("root", "nuc.local") as ssh_client:
        ssh_client.exec_command("cd /root/workspace/; rm ./machines/debby-auto-*")


def stream_stuff(conn, dom):
    def receiver(stream: libvirt.virStream, buf: bytes, opaque: bytearray) -> int:
        # print(buf, end='')
        opaque.extend(buf)
        try:
            print(str(buf, "utf-8"), end="")
        except Exception as _:
            pass

        return len(buf)

    st = conn.newStream(libvirt.VIR_STREAM_NONBLOCK)
    dom.openConsole(None, st)
    st.send(b"whoami\n")
    st.finish()

    buffer = bytearray()
    st = conn.newStream()
    dom.openConsole(None, st)
    res = st.recvAll(receiver, buffer)
    print(res)

    del st


def fileno(file_or_fd):
    fd = getattr(file_or_fd, "fileno", lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stderr_redirected(to=os.devnull, stderr=None):
    if stderr is None:
        stderr = sys.stderr

    stderr_fd = fileno(stderr)
    # copy stderr_fd before it is overwritten
    # NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stderr_fd), "wb") as copied:
        stderr.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stderr_fd)
        except ValueError:
            with open(to, "wb") as to_file:
                os.dup2(to_file.fileno(), stderr_fd)  # $ exec > to
        try:
            yield stderr  # allow code to be run with the redirected stderr
        finally:
            # restore stderr to its previous value
            # NOTE: dup2 makes stderr_fd inheritable unconditionally
            stderr.flush()
            os.dup2(copied.fileno(), stderr_fd)  # $ exec >&copied


def get_random_mac_address():
    # TODO: this raised an `libvirt: Domain Config error : XML error: expected unicast mac address, found multicast '5f:9d:70:a6:67:a6'` exception
    # TODO: read on mac address types

    # return ':'.join([hex(random.randint(0, 255))[2:].zfill(2) for _ in range(6)])
    return "00:00:00:{}:{}:{}".format(
        *[hex(random.randint(0, 255))[2:].zfill(2) for _ in range(3)]
    )
