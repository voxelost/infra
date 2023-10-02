.PHONY: *

_default: deploy clean

ensure-podman:
	- podman machine init --cpus 4 --memory 8096 jellyfin-builder
	- podman machine stop jellyfin-builder
	- podman machine set --rootful jellyfin-builder
	- podman machine start jellyfin-builder

build-images:
	docker compose -f services/build.compose.yml build --pull

push-images: build-images
	docker compose -f services/build.compose.yml push

kompose:
	- mv jellyfin.yml jellyfin.yml.bak
	kompose convert --out=jellyfin.yml --with-kompose-annotation=false

clean:
	- podman machine stop jellyfin-builder

patch-pv:
	$(error patch-pv won't work since StorageClass local-path will always create new PersistentVolumes for PersistentVolumeClaims)
	./tools/pv-patcher.sh

kubectl-apply-build: ensure-podman push-images
	$(info deploying images to dockerhub)
	$(MAKE) kubectl-apply
	$(MAKE) clean

kubectl-apply:
	kubectl apply --recursive -f k8s

kubectl-delete:
	- kubectl delete --recursive -f k8s
