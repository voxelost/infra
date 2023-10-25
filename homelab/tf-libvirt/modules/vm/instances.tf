resource "libvirt_cloudinit_disk" "cloud-init" {
  name  = "${var.suffix}-cloud-init-${count.index + 1}.iso"
  count = var.vm_count
  pool  = var.pool

  user_data = join("\n", [
    var.cloud_init,
    yamlencode({
      hostname : "${var.suffix}-${count.index + 1}"
      ssh_keys : {
        rsa_private : tls_private_key.rsa[count.index].private_key_pem
        rsa_public : tls_private_key.rsa[count.index].public_key_openssh
        ecdsa_private : tls_private_key.ecdsa[count.index].private_key_pem
        ecdsa_public : tls_private_key.ecdsa[count.index].public_key_openssh
        ed25519_private : tls_private_key.ed25519[count.index].private_key_pem
        ed25519_public : tls_private_key.ed25519[count.index].public_key_openssh
      }
    })
  ])
}

resource "libvirt_domain" "vm" {
  name = "${var.suffix}-${count.index + 1}"

  count  = var.vm_count
  vcpu   = var.vcpu
  memory = var.memory

  autostart = var.autostart
  running   = true # Power-off is not currently working

  cpu {
    mode = "host-passthrough"
  }

  boot_device {
    dev = ["hd"]
  }

  network_interface {
    hostname       = "${var.suffix}-${count.index + 1}"
    wait_for_lease = var.network.wait_for_lease

    network_id   = var.network.id
    network_name = var.network.name

    bridge      = var.network.bridge
    vepa        = var.network.vepa
    macvtap     = var.network.macvtap
    passthrough = var.network.passthrough
  }

  disk {
    volume_id = libvirt_volume.boot[count.index].id
  }

  cloudinit  = libvirt_cloudinit_disk.cloud-init[count.index].id
  qemu_agent = true
}
