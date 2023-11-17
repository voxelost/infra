from src.migrations.migration import Migration


class UnmanagedDirectMigration(Migration):
    # https://libvirt.org/migration.html#hypervisor-native-transport

    def begin(self):
        ...
