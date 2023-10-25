variable "suffix" {
  type        = string
  description = "Suffix for VM name"
}

variable "autostart" {
  type        = bool
  default     = false
  description = "Start VMs at boot"
}

variable "vm_count" {
  type        = number
  default     = 1
  description = "Number of VMs to create"
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

variable "cloud_init" {
  type = string
}

variable "boot_image_id" {
  type = string
}

variable "pool" {
  type = string
}

variable "disk_size" {
  type        = number
  default     = 10737418240 # 10GiB
  description = "Disk allocated for the VM, in bytes"
}

variable "network" {
  type = object({
    wait_for_lease = optional(bool, true)
    id             = optional(string)
    name           = optional(string)
    bridge         = optional(string) # "virbr0" # default
    vepa           = optional(string)
    # lsmod | grep macvlan || modprobe macvlan
    # ip link add link enp6s0 name macvtap3 type macvtap mode bridge
    # ip link set macvtap3 up
    # nmcli connection add type macvlan dev enp6s0 mode bridge tap yes ifname macvtap3 con-name macvtap3 ip4 0.0.0.0/24
    macvtap     = optional(string)
    passthrough = optional(string)
  })
}
