import logging
import datetime
from utils.conn import conn_wrapper
from wrappers.domain import Domain
from models.libvirt.snapshot import DomainSnapshot, Name, Description
from utils.dump import setup_logging, destroy_all_vms
from io import StringIO

if __name__ == "__main__":
    setup_logging()

    conn = conn_wrapper()
    if len(conn.listAllDomains()) > 5:
        destroy_all_vms(conn)

    new_dom = Domain.create_default(conn)
    res = new_dom.exec_ssh_cmd("cloud-init status --wait")

    logging.debug(f"cloud init status: {res}")
    logging.debug(f"domain time: {new_dom.getTime()}")

    logging.debug("Creating a snapshot")
    preupload_snapshot = new_dom.create_snapshot()

    with StringIO("hello from controller") as fptr:
        new_dom.upload_file(fptr, "/home/kim/hello")

    res = new_dom.exec_ssh_cmd("cat /home/kim/hello")
    logging.debug(res)

    snapshot_fetched = new_dom.snapshotCurrent()
    assert preupload_snapshot.getXMLDesc() == snapshot_fetched.getXMLDesc()

    logging.debug("Reverting to the snapshot from before file upload")
    new_dom.revertToSnapshot(snapshot_fetched)
    try:
        new_dom.exec_ssh_cmd("cat /home/kim/hello")
    except Exception as e:
        logging.error(e)
