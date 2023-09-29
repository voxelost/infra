.PHONY: *


_default: kubectl-apply
kubectl-apply: kubectl-apply-ddns kubectl-apply-jellyfin kubectl-apply-schedule-observer
kubectl-delete: kubectl-delete-ddns kubectl-delete-jellyfin kubectl-delete-schedule-observer

kubectl-apply-%:
	cd apps/$* && $(MAKE) kubectl-apply

kubectl-delete-%:
	cd apps/$* && $(MAKE) kubectl-delete
