# Setting up NVME for Compute Module 4

Clone eMMC to NVME
```sh
dd if=/dev/mmcblk0 of=/dev/nvme0n1 bs=4MB status=progress
```

<!-- "?TODO: remount /dev/root to nvme" -->

Remount `/boot` under NVME
```sh
umount /boot
mount /dev/nvme0n1p1 /boot
```


Resize new data partition to fill device
```sh
parted ${NVME_DATA_DEVICE} resizepart ${NVME_DATA_PARTITION_NO} 100%
```

e.g.
```sh
parted /dev/nvme0n1 resizepart 2 100%
```


Check new filesystem
```sh
e2fsck -f ${NVME_DATA_PARTITION_DEVICE}
```

e.g.
```sh
e2fsck -f /dev/nvme0n1p2
```


Resize filesystem to fill partition
```sh
resize2fs ${NVME_DATA_PARTITION_DEVICE}
```


e.g.
```sh
resize2fs /dev/nvme0n1p2
```

Mount k3s data dir to the resized partition
```sh
mount ${NVME_DATA_PARTITION_DEVICE} ${K3S_DATA_DIR}
```


e.g.
```sh
mount /dev/nvme0n1p2 /var/lib/rancher/k3s
```

---
# Useful links
- [NotEnoughTech blogpost covering this](https://notenoughtech.com/raspberry-pi/it-took-me-2-months-to-boot-cm4-from-nvme/)

