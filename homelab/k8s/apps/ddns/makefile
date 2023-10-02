.PHONY: *

_default: overwrite_target_platform push

TARGET_PLATFORM=linux/arm
USER=voxelost
REPOSITORY=cloudflare-ddns
VERSION_MAJOR=0
VERSION_MINOR=1
VERSION_PATCH=9
VERSION_SEMVER=${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}
VERSION_TAG=v${VERSION_SEMVER}
IMAGE_TAG=${USER}/${REPOSITORY}:${VERSION_TAG}


build:
	sudo docker build --platform ${TARGET_PLATFORM} --tag ${IMAGE_TAG} .

push: build
	sudo docker push ${IMAGE_TAG}

run: overwrite_target_platform build
	sudo docker run -e AUTH_TOKEN=asdasd -e DNS_ZONE_ID=asdasd -e DNS_RECORD_ID=asdasd -it ${IMAGE_TAG}

overwrite_target_platform:
	$(eval TARGET_PLATFORM = linux/arm64)

kubectl-apply:
	kubectl apply --recursive -f k8s

kubectl-delete:
	- kubectl delete --recursive -f k8s
