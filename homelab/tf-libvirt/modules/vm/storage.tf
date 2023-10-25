resource "libvirt_volume" "boot" {
  name  = "${var.suffix}-boot-${count.index + 1}.qcow2"
  count = var.vm_count
  size  = var.disk_size
  pool  = var.pool

  base_volume_id = var.boot_image_id
}
