vms = {
  kube-master : {
    count : 1
  }
  kube-node : {
    count : 1
  }
}

vcpu   = 1
memory = 2048

pool_dir_path = "/data"

network = {
  bridge : "bridge2"
}
