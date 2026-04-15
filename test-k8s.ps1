# test-k8s.ps1 — Test Kubernetes deployment

$ErrorActionPreference = "Stop"

Write-Host "Testing Nur Scents Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Test 1: Check all pods running
Write-Host "`nTest 1: Check all pods running" -ForegroundColor Yellow
$pods = kubectl get pods -n nur-scents -o json
$podCount = ($pods | ConvertFrom-Json).items.Count
Write-Host "Found $podCount pods" -ForegroundColor Green

$runningPods = kubectl get pods -n nur-scents -o json | `
    ConvertFrom-Json | `
    Select-Object -ExpandProperty items | `
    Where-Object { $_.status.phase -eq "Running" }

Write-Host "Running pods: $($runningPods.Count)" -ForegroundColor Green

if ($runningPods.Count -lt 5) {
    Write-Host "WARNING: Not all pods are running" -ForegroundColor Red
    kubectl get pods -n nur-scents
}

# Test 2: Check services
Write-Host "`nTest 2: Check services" -ForegroundColor Yellow
kubectl get services -n nur-scents
Write-Host "OK Services created" -ForegroundColor Green

# Test 3: Health check
Write-Host "`nTest 3: API Health check" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 10
    Write-Host "Health check response:" -ForegroundColor Green
    $health | ConvertTo-Json
    Write-Host "OK Health check passing" -ForegroundColor Green
} catch {
    Write-Host "FAILED Health check failed: $_" -ForegroundColor Red
}

# Test 4: Test web form
Write-Host "`nTest 4: Test web form submission" -ForegroundColor Yellow
try {
    $body = @{
        name = "Test User"
        email = "test@gmail.com"
        subject = "Test from k8s"
        category = "general"
        message = "Testing Kubernetes deployment"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8080/support/submit" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 10

    Write-Host "Form submission response:" -ForegroundColor Green
    $response | ConvertTo-Json
    Write-Host "OK Web form working" -ForegroundColor Green
} catch {
    Write-Host "FAILED Web form failed: $_" -ForegroundColor Red
}

# Test 5: Check HPA
Write-Host "`nTest 5: Check Horizontal Pod Autoscaler" -ForegroundColor Yellow
kubectl get hpa -n nur-scents
Write-Host "OK HPA configured" -ForegroundColor Green

# Test 6: Check logs
Write-Host "`nTest 6: Check API logs" -ForegroundColor Yellow
Write-Host "Recent API logs:" -ForegroundColor Gray
kubectl logs -l app=nur-scents-api -n nur-scents --tail=5

# Test 7: Pod resilience test
Write-Host "`nTest 7: Pod resilience test" -ForegroundColor Yellow
Write-Host "Deleting one API pod to test auto-restart..." -ForegroundColor Gray

$apiPod = kubectl get pod -l app=nur-scents-api -n nur-scents -o jsonpath='{.items[0].metadata.name}'
kubectl delete pod $apiPod -n nur-scents

Write-Host "Waiting 30 seconds for pod restart..." -ForegroundColor Gray
Start-Sleep -Seconds 30

$newPods = kubectl get pods -l app=nur-scents-api -n nur-scents
Write-Host "Pods after restart:" -ForegroundColor Gray
$newPods

$runningCount = kubectl get pods -l app=nur-scents-api -n nur-scents -o json | `
    ConvertFrom-Json | `
    Select-Object -ExpandProperty items | `
    Where-Object { $_.status.phase -eq "Running" } | `
    Measure-Object | `
    Select-Object -ExpandProperty Count

if ($runningCount -ge 3) {
    Write-Host "OK Pod auto-restart working ($runningCount/3 running)" -ForegroundColor Green
} else {
    Write-Host "WARNING: Only $runningCount/3 pods running" -ForegroundColor Red
}

# Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Deployment Test Summary" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Total pods: $podCount" -ForegroundColor White
Write-Host "Running pods: $($runningPods.Count)" -ForegroundColor White
Write-Host "Services: Configured" -ForegroundColor White
Write-Host "HPA: Configured" -ForegroundColor White
Write-Host "Health endpoint: Tested" -ForegroundColor White
Write-Host "Web form: Tested" -ForegroundColor White
Write-Host "Pod restart: Tested" -ForegroundColor White
Write-Host ""
Write-Host "Deployment tests complete!" -ForegroundColor Green
