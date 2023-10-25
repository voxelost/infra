## Storage
resource "libvirt_pool" "cluster" {
  name = "${var.env}-cluster"
  type = "dir"
  path = "${var.pool_dir_path}/${var.env}-cluster"
}

resource "libvirt_volume" "debian-12-bookworm" {
  name   = "${var.env}-debian-12-bookworm.qcow2"
  pool   = libvirt_pool.cluster.name
  source = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
  # source = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-arm64.qcow2"
}

## VM Instances
module "vms" {
  source    = "./modules/vm"
  for_each  = var.vms
  autostart = var.autostart

  suffix    = "${var.env}-${each.key}"
  vm_count  = each.value.count
  vcpu      = var.vcpu
  memory    = var.memory
  network   = var.network
  disk_size = var.disk_size

  cloud_init    = file("${path.module}/resources/cloud-init.cfg")
  boot_image_id = libvirt_volume.debian-12-bookworm.id
  pool          = libvirt_pool.cluster.name

  depends_on = [libvirt_pool.cluster, libvirt_volume.debian-12-bookworm]
}
