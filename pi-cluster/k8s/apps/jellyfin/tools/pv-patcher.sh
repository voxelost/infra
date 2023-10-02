#!/bin/bash

kubectl get -f k8s/PVC/pvc.yml -o json | jq '.items[].spec.volumeName' -r |
  while read volume_name; do
    kubectl patch pv ${volume_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
  done


