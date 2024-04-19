from utils.models.config import Config

class ThinkpadConfig(Config):
    def __init__(self):
        super().__init__(self)
        self.hostname = 'thinkpad'
        self.script['preseed'].additional_steps = [
            "echo 'HandleLidSwitch=ignore' >> /etc/systemd/logind.conf",
            "echo 'HandleLidSwitchDocked=ignore' >> /etc/systemd/logind.conf",
        ]

        self.network.ethernet_interface_id = 'enp0s25'
