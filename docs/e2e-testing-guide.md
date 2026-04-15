# E2E Testing Guide

## Test Suite Overview

The Nur Scents FTE has **23 comprehensive E2E tests** covering all functionality.

## Prerequisites

1. **FastAPI Running:**
   ```bash
   uvicorn production.api.main:app --reload
   ```

2. **Dependencies Installed:**
   ```bash
   pip install pytest pytest-asyncio httpx pytest-cov
   ```

3. **Optional Services (for full coverage):**
   - PostgreSQL running
   - Kafka running
   - Redis running

## Running Tests

### Quick Test Run
```bash
pytest production/tests/ -v
```

### With Coverage Report
**Windows (PowerShell):**
```powershell
.\run_tests.ps1
```

**Mac/Linux/Git Bash:**
```bash
bash run_tests.sh
```

### Manual Coverage
```bash
pytest production/tests/ \
    --cov=production \
    --cov-report=html:coverage_report \
    --cov-report=term-missing
```

### Specific Test Class
```bash
pytest production/tests/test_multichannel_e2e.py::TestHealthCheck -v
```

### Specific Test
```bash
pytest production/tests/test_multichannel_e2e.py::TestWebFormSubmission::test_valid_form_submission -v
```

## Test Coverage

### 1. Health Check (3 tests)
- ✅ API returns 200
- ✅ Response structure valid
- ✅ All services reported

### 2. Web Form Submission (4 tests)
- ✅ Valid form submission
- ✅ AI response returned
- ✅ Order request handling
- ✅ Complaint handling

### 3. Form Validation (4 tests)
- ✅ Empty name rejected
- ✅ Invalid email rejected
- ✅ Short message rejected
- ✅ Missing fields rejected

### 4. Ticket Status (2 tests)
- ✅ Ticket retrieval
- ✅ Invalid ticket returns 404

### 5. WhatsApp Webhook (3 tests)
- ✅ Webhook accepts message
- ✅ Urdu query handling
- ✅ Empty body handling

### 6. Gmail Webhook (2 tests)
- ✅ Pub/Sub notification handling
- ✅ Empty message handling

### 7. Cross Channel (2 tests)
- ✅ Same customer, different channels
- ✅ Customer lookup by phone

### 8. Order Flow (2 tests)
- ✅ Complete order flow
- ✅ Bulk order escalation

### 9. Owner Commands (3 tests)
- ✅ Channel metrics accessible
- ✅ Owner report requires auth
- ✅ Sales report requires auth

### 10. Escalation Triggers (2 tests)
- ✅ Angry customer escalation
- ✅ Refund request escalation

### 11. Stress Test (2 tests)
- ✅ Multiple concurrent requests
- ✅ API response time < 30s

## Expected Output

```
test_health_endpoint_returns_200 PASSED
test_health_response_structure PASSED
test_health_shows_services PASSED
test_valid_form_submission PASSED
test_form_returns_ai_response PASSED
test_form_handles_order_request PASSED
test_form_handles_complaint PASSED
test_empty_name_rejected PASSED
test_invalid_email_rejected PASSED
test_short_message_rejected PASSED
test_missing_required_fields PASSED
test_whatsapp_webhook_accepts_message PASSED
test_whatsapp_urdu_query PASSED
test_whatsapp_empty_body_handled PASSED
test_gmail_webhook_accepts_notification PASSED
test_same_customer_different_channels PASSED
test_complete_order_flow PASSED
test_bulk_order_triggers_escalation PASSED
test_channel_metrics_accessible PASSED
test_owner_report_requires_auth PASSED
test_angry_customer_escalated PASSED
test_multiple_concurrent_requests PASSED
test_api_response_time PASSED

========================= 23 passed in 45.23s =========================

Coverage Report:
production/api/main.py: 85%
production/agent/customer_success_agent.py: 78%
production/channels/whatsapp_handler.py: 82%
production/channels/gmail_handler.py: 75%
```

## Troubleshooting

### Connection Refused
**Error:** `requests.exceptions.ConnectionError`

**Fix:**
```bash
uvicorn production.api.main:app --reload
```

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'production'`

**Fix:** Run from project root:
```bash
cd nurscents-fte
pytest production/tests/
```

### Timeout Errors
**Error:** `httpx.ConnectTimeout`

**Fix:** Increase timeout in `test_multichannel_e2e.py`:
```python
@pytest.fixture
def client():
    return httpx.Client(
        base_url=BASE_URL,
        timeout=60.0  # Increased from 30.0
    )
```

### Asyncio Errors
**Error:** `asyncio_mode` error

**Fix:** Ensure `pytest.ini` has:
```ini
[pytest]
asyncio_mode = auto
```

### Validation Tests Failing
**Error:** Expected 422 but got 200

**Fix:** Check Pydantic models in `production/api/main.py` have proper validation

## CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Start services
        run: |
          docker-compose up -d
          sleep 30
      - name: Run tests
        run: |
          pytest production/tests/ -v --cov
```

## Best Practices

1. **Run Tests Before Commits:**
   ```bash
   pytest production/tests/ -v
   ```

2. **Check Coverage Regularly:**
   ```bash
   pytest --cov=production --cov-report=html
   ```

3. **Fix Broken Tests Immediately:**
   - Don't commit with failing tests
   - Keep test suite green

4. **Add Tests for New Features:**
   - Every new endpoint needs tests
   - Every new feature needs coverage

5. **Mock External Services:**
   - Use pytest-mock for Twilio
   - Use pytest-mock for Gmail
   - Don't make real API calls in tests

## Coverage Goals

- **Minimum:** 70% coverage
- **Target:** 85% coverage
- **Excellent:** 90%+ coverage

## Next Steps

1. Fix any failing tests
2. Improve coverage for low-coverage files
3. Add integration tests with real services
4. Add performance benchmarks
5. Set up automated testing in CI/CD
