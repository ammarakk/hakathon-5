#!/bin/bash
# teardown.sh — Remove deployment

echo "Removing Nur Scents deployment..."
kubectl delete namespace nur-scents || true
echo "OK Namespace deleted"

echo "Stopping k3d cluster..."
k3d cluster stop nur-scents || true
echo "OK Cluster stopped"
