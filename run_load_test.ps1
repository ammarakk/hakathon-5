# run_load_test.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting Nur Scents Load Test..." -ForegroundColor Cyan
Write-Host ""

# Check API running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK API is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR API not running on port 8000" -ForegroundColor Red
    Write-Host "Start: uvicorn production.api.main:app --reload" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting load test..." -ForegroundColor Yellow
Write-Host "Users: 20 | Spawn rate: 2/sec | Duration: 60s" -ForegroundColor White
Write-Host ""

# Run headless load test
locust `
    -f production/tests/load_test.py `
    --host=http://localhost:8000 `
    --users=20 `
    --spawn-rate=2 `
    --run-time=60s `
    --headless `
    --html=load_test_report.html `
    --csv=load_test_results

Write-Host ""
Write-Host "OK Load test complete!" -ForegroundColor Green
Write-Host "Report: load_test_report.html" -ForegroundColor Cyan
Write-Host "CSV: load_test_results_stats.csv" -ForegroundColor Cyan
