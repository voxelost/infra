output "vms" {
  value = {
    for group, vms in module.vms : group => {
      for vm in vms.vm : vm.name => try(vm.network_interface[0].addresses[0], null) # VMs lose leases when powered off
    }
  }
}
