# tf-libvert

## Notes:
- libvirt provider doesn't work on m1 mac

## Pre-req

```bash
sudo apt install qemu-kvm virt-manager virtinst libvirt-clients bridge-utils libvirt-daemon-system -y
sudo systemctl status libvirtd

# for RPis also
sudo apt-get install qemu-system-arm qemu-efi -y


sudo usermod -aG kvm $USER
sudo usermod -aG libvirt $USER

# launch via `sudo virt-manager`
```

### Fix QEMU permission issues

Set `security_driver = "none"` in `/etc/libvirt/qemu.conf` and restart the service `service libvirtd restart`.
    + https://ostechnix.com/solved-cannot-access-storage-file-permission-denied-error-in-kvm-libvirt/
    + https://askubuntu.com/questions/576437/virsh-ssh-into-a-guest-vm

# NOTE:
```
It worked for me just by adding /data/** rwk, to /etc/apparmor.d/local/abstractions/libvirt-qemu
(/data being my dedicated disk for VM disks)
```


### Create bridge2 network

```bash
export BRIDGE_NETWORK_NAME=
sudo ip link add $BRIDGE_NETWORK_NAME type bridge

export ETHERNET_INTERFACE_ID="enxxxxx"
sudo ip link set $ETHERNET_INTERFACE_ID up
sudo ip link set $ETHERNET_INTERFACE_ID master $BRIDGE_NETWORK_NAME

# verify
sudo ip link show master $BRIDGE_NETWORK_NAME

# add static ip address to bridge
export CIDR_RANGE="192.168.1.80/28"
sudo ip address add dev $BRIDGE_NETWORK_NAME $CIDR_RANGE

# verify that the address was added to the interface
sudo ip addr show $BRIDGE_NETWORK_NAME
```

## Pre-req (on machine you're running terraform)
```bash
sudo apt install mkisofs -y
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| terraform | ~> 1.5 |
| libvirt | 0.7.1 |
| local | >= 2.4.0 |

## Providers

| Name | Version |
|------|---------|
| libvirt | 0.7.1 |
| local | 2.4.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| vms | ./modules/vm | n/a |

## Resources

| Name | Type |
|------|------|
| [libvirt_pool.cluster](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/pool) | resource |
| [libvirt_volume.debian-12-bookworm](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/volume) | resource |
| [local_file.kubespray-inventory](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| autostart | Start VMs at boot | `bool` | `false` | no |
| disk\_size | Disk allocated for the VM, in bytes | `number` | `10737418240` | no |
| env | Environment name (prefix) | `string` | `"local"` | no |
| memory | RAM allocated for the VM, in megabytes | `number` | `512` | no |
| network | n/a | ```object({ wait_for_lease = optional(bool, true) id = optional(string) name = optional(string) bridge = optional(string) vepa = optional(string) macvtap = optional(string) passthrough = optional(string) })``` | n/a | yes |
| pool\_dir\_path | Volume pool path for VM disks | `string` | `"/var/lib/libvirt/images"` | no |
| vcpu | CPU cores allocated for the VM | `number` | `1` | no |
| vms | n/a | ```map(object({ count = number }))``` | ```{ "master": { "count": 1 }, "node": { "count": 1 } }``` | no |

## Outputs

| Name | Description |
|------|-------------|
| vms | n/a |
<!-- END_TF_DOCS -->
