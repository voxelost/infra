import libvirt
from utils.default_helpers.default_debian import get_default_machine
from utils.conn import conn_wrapper
from wrappers.domain import Domain

def try_destroy_all_vms(conn: libvirt.virConnect=None):
    if conn is None:
        conn = conn_wrapper()
        import atexit
        atexit.register(conn.close)
    doms = conn.listAllDomains()
    for dom in doms:
        try:
            dom.destroy()
        except Exception as _:
            try:
                dom.undefine()
            except Exception as e:
                print(e)

    import paramiko
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy)
    ssh_client.connect('nuc.local', username='root', pkey=paramiko.PKey.from_path('/Users/voxelost/workspace/devops/infra/homelab/vm-manager/nuc.pem'))
    ssh_client.exec_command('cd /root/workspace/; rm debby-auto-*')

def stream_stuff(conn, dom):
    def receiver(stream: libvirt.virStream, buf: bytes, opaque: bytearray) -> int:
        # print(buf, end='')
        opaque.extend(buf)
        # if str(opaque, 'utf-8').endswith('debian login: '):
        #     return -1

        try:
            print(str(buf, 'utf-8'), end='')
        except Exception as _:
            pass

        return len(buf)

    st = conn.newStream(libvirt.VIR_STREAM_NONBLOCK)
    dom.openConsole(None, st)
    st.send(b'whoami\n')
    st.finish()


    buffer = bytearray()
    st = conn.newStream()
    dom.openConsole(None, st)
    res = st.recvAll(receiver, buffer)
    print(res)

    del st

if __name__ == "__main__":
    # with conn_wrapper() as conn:
    #     if len(conn.listAllDomains()) > 5:
    #         try_destroy_all_vms(conn)

    #     new_dom = Domain(conn.createXML(get_default_machine().to_xml_string()))

    import paramiko
    def connect(host, user, pkey, gateway=None):
        client = paramiko.SSHClient()
        sock = None
        if gateway:
            gw_client = connect(gateway, user, pkey)
            sock = gw_client.get_transport().open_channel(
                'direct-tcpip', (host, 22), ('', 0)
            )
        kwargs = dict(
            port=22,
            username=user,
            pkey=pkey,
            sock=sock,
        )
        client.connect(host, **kwargs)
        return client

    client = connect(
        '192.168.122.49',
        'root',
        paramiko.PKey.from_path('/Users/voxelost/workspace/devops/infra/homelab/vm-manager/nuc.pem'),
        'nuc.local',
    )

    client.exec_command('ls -la')
    client.close()
