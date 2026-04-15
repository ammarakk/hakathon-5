#!/bin/bash
# run_tests.sh — Run all E2E tests

echo "Running Nur Scents E2E Tests..."
echo "Make sure FastAPI is running on port 8000"
echo ""

# Check API is running
if ! curl -s http://localhost:8000/health \
    > /dev/null 2>&1; then
    echo "ERROR FastAPI not running!"
    echo "Start with:"
    echo "uvicorn production.api.main:app --reload"
    exit 1
fi

echo "OK API is running"
echo ""

# Run all tests
pytest production/tests/ \
    -v \
    --tb=short \
    --cov=production \
    --cov-report=term-missing \
    --cov-report=html:coverage_report \
    -x

echo ""
echo "Coverage report: coverage_report/index.html"
