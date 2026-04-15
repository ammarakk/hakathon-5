# teardown.ps1 — Remove deployment (PowerShell)

Write-Host "Removing Nur Scents deployment..." -ForegroundColor Yellow
kubectl delete namespace nur-scents -ErrorAction SilentlyContinue
Write-Host "OK Namespace deleted" -ForegroundColor Green

Write-Host "Stopping k3d cluster..." -ForegroundColor Yellow
k3d cluster stop nur-scents -ErrorAction SilentlyContinue
Write-Host "OK Cluster stopped" -ForegroundColor Green
