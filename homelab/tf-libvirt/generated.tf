## Generated content
locals { # this needs to stay here
  vms = flatten([
    for group, vms in module.vms : [
      for vm in vms.vm : {
        name : vm.name
        group : group
        ip : vm.network_interface[0].addresses[0]
      } if can(vm.network_interface[0].addresses[0]) # Do not pass VMs with no network to Ansible
    ]
  ])
  masters = [for vm in local.vms : vm if strcontains(vm.group, "master")]
  nodes   = [for vm in local.vms : vm if strcontains(vm.group, "node")]
}

resource "local_file" "kubespray-inventory" {
  content = templatefile("${path.module}/resources/kubespray/inventory.yaml.tftpl", {
    vms     = local.vms
    masters = local.masters
    nodes   = local.nodes
  })

  filename = "generated/kubespray/inventory.yaml"

  depends_on = [module.vms]
}
