.PHONY: *

_default: provision-cluster download-kubeconfig

provision-cluster:
	cd ansible/provisioning/k3s/CM4 && $(MAKE)

download-kubeconfig:
	cd ansible/provisioning/k3s/CM4/ && $(MAKE) download-kubeconfig
	- rm -rf k8s/.kube.bak
	- mv k8s/.kube k8s/.kube.bak
	mv ansible/provisioning/k3s/CM4/.kube.tmp k8s/.kube

kubectl-apply:
	cd k8s && $(MAKE) kubectl-apply

kubectl-delete:
	cd k8s && $(MAKE) kubectl-delete
