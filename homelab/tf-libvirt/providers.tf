provider "libvirt" {
  # uri = "qemu+ssh://root@192.168.18.53/system?keyfile=/Users/voxelost/workspace/devops/infra/homelab/tf-libvirt/nuc.pem"

  # tf doesn't resolve by hostname.local
  uri = "qemu+ssh://root@192.168.18.53/system?keyfile=./nuc.pem&sshauth=privkey&no_verify=1"
}

# user debian must be in group libvirt
