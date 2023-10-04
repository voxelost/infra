.PHONY: *

_default: deploy clean

ensure-podman: MACHINE_CPUS ?= 4
ensure-podman: MACHINE_MEMORY ?= 8096
ensure-podman:
	- podman machine init --cpus ${MACHINE_CPUS} --memory ${MACHINE_MEMORY} ${MACHINE_NAME}
	- podman machine stop ${MACHINE_NAME}
	- podman machine set --rootful ${MACHINE_NAME}
	- podman machine start ${MACHINE_NAME}

build-images:
	docker compose -f services/build.compose.yml build --pull

push-images: build-images
	docker compose -f services/build.compose.yml push

kompose:
	- mv jellyfin.yml jellyfin.yml.bak
	kompose convert --out=jellyfin.yml --with-kompose-annotation=false

dashboard:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
	kubectl apply -f dev/ServiceAccount/sa.yml

dashboard-token: dashboard
	$(info dashboard token is:)
	@kubectl get secret admin-user -n kubernetes-dashboard -o jsonpath={".data.token"} | base64 -d
	@printf '\n########################################################################\n'

proxy:
	kubectl proxy

dev:
	MACHINE_CPUS=6 MACHINE_NAME=kind-cluster $(MAKE) ensure-podman
	- kind create cluster --config dev/kind-config.yml
	$(MAKE) kubectl-apply
	$(MAKE) dashboard
	$(MAKE) dashboard-token
	$(MAKE) proxy

clean:
	- podman machine stop jellyfin-builder
	- podman machine rm jellyfin-builder <<< 'y'
	- kind delete cluster
	- podman machine stop kind-cluster
	- podman machine rm kind-cluster <<< 'y'

patch-pv:
	$(error patch-pv won't work since StorageClass local-path will always create new PersistentVolumes for PersistentVolumeClaims)
	./tools/pv-patcher.sh

kubectl-apply-build:
	MACHINE_NAME=jellyfin-builder $(MAKE) ensure-podman
	$(MAKE) push-images
	$(info deploying images to dockerhub)
	$(MAKE) kubectl-apply
	$(MAKE) clean

kubectl-apply:
	kubectl apply --recursive -f k8s

kubectl-delete:
	- kubectl delete --recursive -f k8s
