# run_tests.ps1 — Run all E2E tests (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "Running Nur Scents E2E Tests..." -ForegroundColor Cyan
Write-Host "Make sure FastAPI is running on port 8000" -ForegroundColor Yellow
Write-Host ""

# Check API is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK API is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR FastAPI not running!" -ForegroundColor Red
    Write-Host "Start with:" -ForegroundColor Yellow
    Write-Host "uvicorn production.api.main:app --reload" -ForegroundColor White
    exit 1
}

Write-Host ""

# Run all tests
pytest production/tests/ `
    -v `
    --tb=short `
    --cov=production `
    --cov-report=term-missing `
    --cov-report=html:coverage_report

Write-Host ""
Write-Host "Coverage report: coverage_report/index.html" -ForegroundColor Cyan
