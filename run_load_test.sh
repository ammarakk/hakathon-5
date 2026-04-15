#!/bin/bash
# run_load_test.sh

echo "Starting Nur Scents Load Test..."
echo ""

# Check API running
if ! curl -s http://localhost:8000/health \
    > /dev/null 2>&1; then
    echo "ERROR API not running on port 8000"
    echo "Start: uvicorn production.api.main:app --reload"
    exit 1
fi

echo "OK API is running"
echo ""
echo "Starting load test..."
echo "Users: 20 | Spawn rate: 2/sec | Duration: 60s"
echo ""

# Run headless load test
locust \
    -f production/tests/load_test.py \
    --host=http://localhost:8000 \
    --users=20 \
    --spawn-rate=2 \
    --run-time=60s \
    --headless \
    --html=load_test_report.html \
    --csv=load_test_results

echo ""
echo "OK Load test complete!"
echo "Report: load_test_report.html"
echo "CSV: load_test_results_stats.csv"
