#!/bin/bash
# deploy.sh — Deploy Nur Scents to k3d

set -e

echo "Deploying Nur Scents CRM to k3d..."

# Check k3d cluster exists
if ! k3d cluster list | grep -q "nur-scents"; then
    echo "Creating k3d cluster..."
    k3d cluster create nur-scents \
        --port "8080:80@loadbalancer" \
        --agents 2
    echo "OK Cluster created"
else
    echo "OK Cluster exists"
fi

# Build images
echo "Building Docker images..."
docker build -t nur-scents-api:latest . -q
docker build -f Dockerfile.worker \
    -t nur-scents-worker:latest . -q
echo "OK Images built"

# Import to k3d
echo "Importing images to k3d..."
k3d image import nur-scents-api:latest \
    -c nur-scents
k3d image import nur-scents-worker:latest \
    -c nur-scents
echo "OK Images imported"

# Apply manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/redis.yaml

echo "Waiting for databases (30s)..."
sleep 30

kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

echo "OK Manifests applied"

# Wait for pods
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    -l app=nur-scents-api \
    -n nur-scents \
    --timeout=120s || true

# Show status
echo ""
echo "Deployment Status:"
kubectl get pods -n nur-scents
echo ""
echo "Services:"
kubectl get services -n nur-scents
echo ""
echo "OK Deployment complete!"
echo ""
echo "Access API at: http://localhost:8080"
echo "Health check: http://localhost:8080/health"
