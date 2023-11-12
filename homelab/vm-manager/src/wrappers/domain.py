import time
from libvirt import virDomain, VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT
from typing import Optional


class Domain(virDomain):
    def __init__(self, vd: virDomain):
        self._proxied = vd

    def __getattr__(self, name: str):
        return getattr(self._proxied, name)

    def get_ip(self, tries: int = 50) -> Optional[str]:
        addresses = []
        for i in range(tries):
            try:
                addresses = self._proxied.interfaceAddresses(VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
                break
            except Exception as _:
                print(f'[{i+1}/{tries}] waiting for qemu-guest-agent to start...')
                time.sleep(5)
                continue
        else:
            print("qemu-user-agent didn't start on time")

        for addr in addresses['enp1s0']['addrs']:
            if addr['type'] == 0: # address type ipv4
                return addr['addr']

        print("couldn't find machine ip address")
        return None
