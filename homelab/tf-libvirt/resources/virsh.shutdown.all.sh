#!/bin/bash
echo "=== shutting down all kvm vms ==="
for i in $(virsh list | grep running | awk '{print $2}'); do
    virsh shutdown $i;
done

virsh list --all
