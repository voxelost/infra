from src.migrations.migration import Migration


class HypervisorNativeMigration(Migration):
    # https://libvirt.org/migration.html#hypervisor-native-transport

    def begin(self):
        ...
