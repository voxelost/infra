resource "tls_private_key" "rsa" {
  count     = var.vm_count
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "tls_private_key" "ecdsa" {
  count       = var.vm_count
  algorithm   = "ECDSA"
  ecdsa_curve = "P384"
}

resource "tls_private_key" "ed25519" {
  count     = var.vm_count
  algorithm = "ED25519"
}
