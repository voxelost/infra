output "vm" {
  value = libvirt_domain.vm[*]
}
