# deploy.ps1 — Deploy Nur Scents to k3d (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "Deploying Nur Scents CRM to k3d..." -ForegroundColor Green

# Check k3d cluster exists
$clusterExists = k3d cluster list | Select-String "nur-scents"
if (-not $clusterExists) {
    Write-Host "Creating k3d cluster..." -ForegroundColor Yellow
    k3d cluster create nur-scents --port "8080:80@loadbalancer" --agents 2
    Write-Host "OK Cluster created" -ForegroundColor Green
} else {
    Write-Host "OK Cluster exists" -ForegroundColor Green
}

# Build images
Write-Host "Building Docker images..." -ForegroundColor Yellow
docker build -t nur-scents-api:latest . -q
docker build -f Dockerfile.worker -t nur-scents-worker:latest . -q
Write-Host "OK Images built" -ForegroundColor Green

# Import to k3d
Write-Host "Importing images to k3d..." -ForegroundColor Yellow
k3d image import nur-scents-api:latest -c nur-scents
k3d image import nur-scents-worker:latest -c nur-scents
Write-Host "OK Images imported" -ForegroundColor Green

# Apply manifests
Write-Host "Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/redis.yaml

Write-Host "Waiting for databases (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

Write-Host "OK Manifests applied" -ForegroundColor Green

# Wait for pods
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=nur-scents-api -n nur-scents --timeout=120s -ErrorAction SilentlyContinue

# Show status
Write-Host ""
Write-Host "Deployment Status:" -ForegroundColor Cyan
kubectl get pods -n nur-scents
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
kubectl get services -n nur-scents
Write-Host ""
Write-Host "OK Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Access API at: http://localhost:8080" -ForegroundColor White
Write-Host "Health check: http://localhost:8080/health" -ForegroundColor White
