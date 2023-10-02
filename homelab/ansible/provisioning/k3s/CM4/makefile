.PHONY: *

_default: reset provision

reset:
	$(info "resetting cluster")
	ansible-playbook reset.yml -i inventory/cluster/hosts.ini

provision:
	$(info "provisioning cluster")
	ansible-playbook setup.yml -i inventory/cluster/hosts.ini

download-kubeconfig:
	$(info "downloading ~/.kube directory")
	- rm -rf .kube.tmp
	scp -r pi@master.local:~/.kube .kube.tmp
