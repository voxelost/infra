<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Contents

- [Introduction](#introduction)
- [Compatibility](#compatibility)
- [Prerequisites (Hypervisor)](#prerequisites-hypervisor)
- [Prerequisites (on machine you're running terraform)](#prerequisites-on-machine-youre-running-terraform)
- [Usage](#usage)
- [Configuration](#configuration)
- [SSH Users](#ssh-users)
- [Generated files](#generated-files)
- [Storage](#storage)
  - [Storage pool](#storage-pool)
  - [Important notes on AppArmor](#important-notes-on-apparmor)
  - [Volumes](#volumes)
- [Networking](#networking)
  - [Virtual libvirt network](#virtual-libvirt-network)
  - [Bridge network](#bridge-network)
  - [Macvtap network](#macvtap-network)
  - [Other networks](#other-networks)
- [Config management (cloud-init)](#config-management-cloud-init)
- [Troubleshooting](#troubleshooting)
- [Known issues](#known-issues)
- [Requirements](#requirements)
- [Providers](#providers)
- [Resources](#resources)
- [Inputs](#inputs)
- [Outputs](#outputs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This project is a simplified abstraction for **libvirt** and **KVM/QEMU** using **Terraform**.
It allows you to create and manage a cluster of VMs at home or on any baremetal machine supporting KVM/QEMU.
It enables full **Infrastructure as Code (IaC)** workflow without renting instances from cloud providers.

## Compatibility

- libvirt provider currently doesn't work on Apple ARM M1/M2/M3 Macs
- Tested on Debian based hypervisor with 100 overprovisioned VMs
- Non-Debian distros will work, but some packages might be named differently and QEMU might be using SELinux instead of AppArmor.
- Terraform 1.5+ is supported. OpenTofu will be supported as soon as it releases stable version.
- Tested VM guest OS distros - Debian 12, Ubuntu 22.04, Rocky Linux 9.2, AlmaLinux 9.2, Fedora 38

## Prerequisites (Hypervisor)

- Install dependencies:

```bash
sudo apt install qemu-kvm virtinst libvirt-clients bridge-utils libvirt-daemon-system -y
```

- Check if libvirt is up: `libvirtd libvirtd status`
- Verify that the machine has virtualization correctly set up: `sudo virt-host-validate qemu`
- To be able to interact with `virsh` and KVM, you may want to add your user to its groups and relaunch shell session:

```bash
sudo usermod -aG kvm $USER
sudo usermod -aG libvirt $USER
```

- You may also want to minimize hypervisor's swap usage:

```bash
sudo sysctl -w vm.swappiness=1
# Persist with
echo 'vm.swappiness = 1' | sudo tee -a /etc/sysctl.d/99-sysctl-swappiness.conf
sudo sysctl -p /etc/sysctl.d/99-sysctl-swappiness.conf
```

## Prerequisites (on machine you're running terraform)

Note: this can be the same machine with KVM/QEMU hypervisor

- [Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) or use [tfenv](https://github.com/tfutils/tfenv)
- Install dependencies:

```bash
sudo apt install mkisofs xsltproc -y
```

- In case you want a desktop GUI for VMs:

```bash
sudo apt install virt-manager -y
```

[//]: # (TODO: Add info for connecting to remote machine from `providers.tf`)

## Usage

- `cp vms.auto.tfvars.example vms.auto.tfvars` then [adjust config](#configuration) for the hardware you're using.
- Initialize terraform:

```bash
terraform init
```

- Plan and apply the changes:

```bash
terraform plan
terraform apply
```

- After you're done testing, you can delete and clean everything up with:

```bash
terraform destroy
```

## Configuration

VM groups and resource allocations are defined in `vms` setting.

#### Example of minimal config:

```text
vms = {
  instance : {
    count : 1
  }
}
```

For each defined group of VMs you can add the following config values to override globally set ones:

- `vcpu`
- `memory`
- `boot_image`
- `boot_disk_size`
- `volumes`
- `network`
- `packages`
- `cloud_init`
- `users`

See [Inputs](#inputs) for more info.

## SSH Users

By default, all `.pub` files from `resources/ssh-users` directory are used by cloud-init to create a user for each file.
Usernames are matching the base filename, with any amount of SSH keys (one per line) found in the file.

Additionally, you can set `home_ssh_keys` to `true` if you want to read all SSH public keys for your user from `~/.ssh`

It is also possible to create/modify users by setting `users` with any parameters [supported by cloud-init](https://cloudinit.readthedocs.io/en/latest/reference/modules.html#users-and-groups).

## Generated files

Multiple files containing host information can be generated to interact with your cluster after creation:

- `hosts` file containing list of created ips and hostnames. Useful for adding to `/etc/hosts`
- `inventory.yaml` for Ansible inventory in suitable format for Kubespray

Enable file generation by setting `generate_files` to `true`. By default, files will be placed in `artifacts/` directory.
Set custom paths with `files`.

In addition, it is possible to manage SSH config at `~/.ssh/config` by setting `populate_ssh_config` to `true`.
This enables you to autocomplete SSH hosts without modifying any DNS and ensures host keys are correct.

## Storage

### Storage pool

With no `pool_dir_path` configuration provided, `default` libvirt storage pool is used at `/var/lib/libvirt/images`.
Set it to any desired location for creating new storage pool containing all the VM disk volumes.

### Important notes on AppArmor

Setting custom paths can cause issues with AppArmor policies and fail with permission errors.
You can verify if it's AppArmor related by looking for denied operations in `dmesg` or syslog.
This is a known issue with Debian's AppArmor profiles for QEMU.

To fix it, you can modify `/etc/apparmor.d/local/abstractions/libvirt-qemu` file with:

```text
/<your-custom-path>/** rwk,
```

Alternatively you can disable VM security completely by setting `security_driver = "none"` in `/etc/libvirt/qemu.conf`. (Not recommended)

Make sure you restart libvirt with `service libvirtd restart` after any of these changes.

### Volumes

Boot volume will be created with size defined in `boot_disk_size` (default 10GiB).
You can add additional volumes by configuring `volumes` setting.
These will be formatted and auto-mounted by cloud-init.

## Networking

With no `network` configuration provided, `default` libvirt network is used.

### Virtual libvirt network

Virtual networks managed by libvirt use default `virbr0` bridge to create a network with host machine using virtual NAT with DHCP server.

You can create your own by using `virt-manager` and configuring `network: {name: "<name>"}`
or by creating `network.tf` file with [`libvirt_network` resource](https://registry.terraform.io/providers/dmacvicar/libvirt/latest/docs/resources/network) and configuring `network: {id: libvirt_network.<name>.id}`.

#### Example `network.tf` file:

```hcl
resource "libvirt_network" "cluster-net" {
  name = "${var.env}-cluster-net"
  mode = "nat"
  addresses = ["10.17.3.0/24"]
  dns {
    enabled = true
  }
}
```

#### Note

Virtual networks create connectivity only with the hypervisor host.
This is the slowest network type but easy to use and is most compatible.
You may need to add VMs in small batches, or sometimes they don't get leases and timeout on creation.

See [libvirt virtual networking docs](https://wiki.libvirt.org/VirtualNetworking.html) for more info.

### Bridge network

Bridge network is recommended option in most cases.
It exposes the VMs to network attached to the host machine.
It requires a bridge interface on host machine.

#### Example on how to create one:

```bash
export BRIDGE_NETWORK_NAME=bridge0
sudo ip link add $BRIDGE_NETWORK_NAME type bridge

export ETHERNET_INTERFACE_ID="enxxxx"
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

#### Note

See docs of the host machine's distro for persisting the bridge configuration.

### Macvtap network

Macvtap offers the best performance but isolates the host from connecting VMs directly.
Host machine can connect to VMs through attached network hardware if its configuration supports it.
Useful for multiple NICs.

#### Example:

```bash
# load required kernel module
lsmod | grep macvlan || modprobe macvlan

export MACVTAP_NAME=macvtap0
export ETHERNET_INTERFACE_ID="enxxxx"
ip link add link $ETHERNET_INTERFACE_ID name $MACVTAP_NAME type macvtap mode bridge
ip link set $MACVTAP_NAME up
```

### Other networks

VEPA and passthrough are possible if your network hardware supports it.

## Config management (cloud-init)

Currently `cloud-init` is used to implement basic automation that manages the following config for each VM at creation:

- Upgrading the OS
- Setting hostname
- Generating SSH host keys (used with `populate_ssh_config`)
- Configuring [SSH users](#ssh-users)
- Installing `qemu-guest-agent` and any additional packages set in `packages`
- In case any additional `volumes` are defined:
  - Matching block device with serial added by XSLT
  - Initializing empty volumes with GPT and formatting them
  - Partitioning volumes with EXT4 or specified `volume: {filesystem: "<filesystem>"}`
  - Mounting volumes and configuring `/etc/fstab`
  - Setting up `growpart`

Global static cloud-config file can be found at `resources/cloud-init.cfg`.

It is also possible to set `cloud_init` to provide extra config globally or per VM group in `vms`.

See [cloud-init examples](https://cloudinit.readthedocs.io/en/latest/reference/examples.html) for more info.

## Troubleshooting

#### VM instances timeout on creation

This is most likely a network issue, caused by DHCP failing to issue a lease or IP lease pool being full.
It means that cloud-init has failed to install `qemu-guest-agent` package.
It can be caused by misconfigured cloud-config, guest's package manager failing to fetch repos or broken dependencies.
It can also be caused by using a base image that doesn't include `cloud-init` and therefore has no support for custom userdata.

## Known issues

#### VMs not powering off from terraform

This seems to be an issue with libvirt provider and/or some KVM setups.
Setting `running` to `false` works only if your VMs are already powered off.
You can shut them all down by using the included `resources/virsh.shutdown.all.sh` script or simply `make stop-vms`.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| terraform | ~> 1.5 |
| libvirt | 0.7.1 |
| local | >= 2.4.0 |
| null | >= 3.2.1 |
| tls | >= 4.0.4 |

## Providers

| Name | Version |
|------|---------|
| libvirt | 0.7.1 |
| local | 2.4.0 |
| null | 3.2.1 |
| tls | 4.0.4 |

## Resources

| Name | Type |
|------|------|
| [libvirt_cloudinit_disk.cloud_init](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/cloudinit_disk) | resource |
| [libvirt_domain.instance](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/domain) | resource |
| [libvirt_pool.cluster](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/pool) | resource |
| [libvirt_volume.boot_disk](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/volume) | resource |
| [libvirt_volume.boot_image](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/volume) | resource |
| [libvirt_volume.volume](https://registry.terraform.io/providers/dmacvicar/libvirt/0.7.1/docs/resources/volume) | resource |
| [local_file.hosts](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.known_hosts](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.kubespray_inventory](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.ssh_config](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [null_resource.ssh_config](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [tls_private_key.ecdsa](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key) | resource |
| [tls_private_key.ed25519](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key) | resource |
| [tls_private_key.rsa](https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| autostart | Start all VMs at boot | `bool` | `false` | no |
| boot\_disk\_size | Boot disk allocated for the VM, in bytes | `number` | `10737418240` | no |
| boot\_image | Image from `images` to use for booting | `string` | `"debian-12"` | no |
| cloud\_init | Custom [cloud-init](#config-management-cloud-init) config map | `any` | `{}` | no |
| device\_prefix | Disk device name prefix for automatic formatting/mounting by [cloud-init](#config-management-cloud-init) | `string` | `"/dev/disk/by-id/virtio-"` | no |
| env | Environment name (prefix) | `string` | `"local"` | no |
| files | Paths for generated files (see [Generated Files](#generated-files) for more info) | ```object({ hosts = optional(string, "artifacts/hosts") known_hosts = optional(string, "artifacts/known_hosts") ssh_config = optional(string, "artifacts/ssh_config") kubespray_inventory = optional(string, "artifacts/kubespray/inventory.yaml") })``` | `{}` | no |
| generate\_files | Generate cluster info files | `bool` | `false` | no |
| home\_ssh\_keys | Search for user's SSH keys in `~/.ssh/*.pub` | `bool` | `false` | no |
| host\_passthrough | Enable Host passthrough CPU mode for VM | `bool` | `false` | no |
| images | Map of image sources | `map(string)` | ```{ "alma-9": "https://repo.almalinux.org/almalinux/9/cloud/x86_64/images/AlmaLinux-9-GenericCloud-latest.x86_64.qcow2", "arch": "https://linuximages.de/openstack/arch/arch-openstack-LATEST-image-bootstrap.qcow2", "debian-12": "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2", "fedora-38": "https://download.fedoraproject.org/pub/fedora/linux/releases/38/Cloud/x86_64/images/Fedora-Cloud-Base-38-1.6.x86_64.qcow2", "rocky-9": "https://download.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2", "ubuntu-22": "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64-disk-kvm.img" }``` | no |
| memory | RAM allocated for the VM, in megabytes | `number` | `1024` | no |
| network | Networking options (see [Networking](#networking) section for more info) | ```object({ wait_for_lease = optional(bool, true) id = optional(string) name = optional(string) bridge = optional(string) vepa = optional(string) macvtap = optional(string) passthrough = optional(string) })``` | ```{ "bridge": null, "id": null, "macvtap": null, "name": "default", "passthrough": null, "vepa": null, "wait_for_lease": true }``` | no |
| packages | List of packages to install by [cloud-init](#config-management-cloud-init) | `list(string)` | `[]` | no |
| pool\_dir\_path | Custom volume pool path for VMs (see [Storage](#storage) section for more info) | `string` | `null` | no |
| populate\_ssh\_config | Add SSH hosts to `~/.ssh/config` | `bool` | `false` | no |
| running | Set running state of all VMs | `bool` | `true` | no |
| ssh\_users\_path | Path to ssh keys with username as filename to create by [cloud-init](#config-management-cloud-init) | `string` | `"resources/ssh-users"` | no |
| users | Users to create by cloud-init (see [SSH Users](#ssh-users) section for more info) | `map(any)` | `{}` | no |
| vcpu | CPU cores allocated for the VM | `number` | `1` | no |
| vms | Main config map of VM groups. (see [Configuration](#configuration) section for more info) | `any` | ```{ "master": { "count": 0 }, "node": { "count": 1 } }``` | no |
| volumes | Additional disk volumes managed by [cloud-init](#config-management-cloud-init) | ```map(object({ mountpoint = string filesystem = optional(string, "ext4") size = optional(number, 10737418240) # 10GiB }))``` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| vms | Map of hostnames and IPs (once VMs get a lease) |
<!-- END_TF_DOCS -->
