variable "env" {
  type        = string
  default     = "local"
  description = "Environment name (prefix)"
}

variable "vms" {
  type = map(object({
    count = number
  }))
  default = {
    master : {
      count : 1
    },
    node : {
      count : 1
    }
  }
}

variable "autostart" {
  type        = bool
  default     = false
  description = "Start VMs at boot"
}

variable "vcpu" {
  type        = number
  default     = 1
  description = "CPU cores allocated for the VM"
}

variable "memory" {
  type        = number
  default     = 512
  description = "RAM allocated for the VM, in megabytes"
}

variable "disk_size" {
  type        = number
  default     = 10737418240 # 10GiB
  description = "Disk allocated for the VM, in bytes"
}

variable "pool_dir_path" {
  type        = string
  default     = "/var/lib/libvirt/images"
  description = "Volume pool path for VM disks"
}

variable "network" {
  type = object({
    wait_for_lease = optional(bool, true)
    id             = optional(string)
    name           = optional(string)
    bridge         = optional(string)
    vepa           = optional(string)
    macvtap        = optional(string)
    passthrough    = optional(string)
  })
}
