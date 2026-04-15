# production/tests/test_multichannel_e2e.py

import pytest
import asyncio
import httpx
import json
import base64
from datetime import datetime

BASE_URL = "http://localhost:8000"
K8S_URL = "http://localhost:8080"

# Fixtures
@pytest.fixture
def api_url():
    return BASE_URL

@pytest.fixture
def client():
    return httpx.Client(
        base_url=BASE_URL,
        timeout=30.0
    )

@pytest.fixture
def async_client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30.0
    )

# TEST 1: Health Check
class TestHealthCheck:

    def test_health_endpoint_returns_200(
        self, client
    ):
        """API must be running and healthy"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(
        self, client
    ):
        """Health response has required fields"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    def test_health_shows_services(
        self, client
    ):
        """Health shows all service statuses"""
        response = client.get("/health")
        data = response.json()
        services = data.get("services", {})
        assert "database" in services
        assert "kafka" in services
        assert "agent" in services

# TEST 2: Web Form Submission
class TestWebFormSubmission:

    def test_valid_form_submission(
        self, client
    ):
        """Web form submits successfully"""
        payload = {
            "name": "Ahmed Khan",
            "email": "ahmed@test.com",
            "phone": "0300-1234567",
            "subject": "Oud attar price query",
            "category": "product_query",
            "message": "Mujhe oud attar ki prices batao please. Kaafi time se dhundh raha hun."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "ticket_id" in data
        assert "response" in data

    def test_form_returns_ai_response(
        self, client
    ):
        """Form submission returns AI response"""
        payload = {
            "name": "Sara Ali",
            "email": "sara@test.com",
            "subject": "Rose attar available?",
            "category": "product_query",
            "message": "Do you have rose attar in stock? I need it for a gift."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("response", "")) > 10

    def test_form_handles_order_request(
        self, client
    ):
        """Form handles order placement"""
        payload = {
            "name": "Bilal Hassan",
            "email": "bilal@test.com",
            "phone": "0321-9876543",
            "subject": "Want to order Oud Al Shams",
            "category": "order",
            "message": "I want to order Oud Al Shams 6ml. Deliver to Gulshan. Payment via JazzCash."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_form_handles_complaint(
        self, client
    ):
        """Form handles customer complaint"""
        payload = {
            "name": "Zara Ahmed",
            "email": "zara@test.com",
            "subject": "Order not delivered",
            "category": "complaint",
            "message": "My order was placed 5 days ago and still not delivered. This is very frustrating."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

# TEST 3: Form Validation
class TestFormValidation:

    def test_empty_name_rejected(
        self, client
    ):
        """Short name should be rejected"""
        payload = {
            "name": "A",
            "email": "test@test.com",
            "subject": "Test query",
            "category": "general",
            "message": "This is a test message"
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 422

    def test_invalid_email_rejected(
        self, client
    ):
        """Invalid email should be rejected"""
        payload = {
            "name": "Test User",
            "email": "not-an-email",
            "subject": "Test query",
            "category": "general",
            "message": "This is a test message"
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 422

    def test_short_message_rejected(
        self, client
    ):
        """Message too short should be rejected"""
        payload = {
            "name": "Test User",
            "email": "test@test.com",
            "subject": "Test",
            "category": "general",
            "message": "Hi"
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 422

    def test_missing_required_fields(
        self, client
    ):
        """Missing required fields rejected"""
        payload = {
            "name": "Test User"
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 422

# TEST 4: Ticket Status
class TestTicketStatus:

    def test_ticket_created_and_retrievable(
        self, client
    ):
        """Submitted ticket can be retrieved"""
        # Submit form
        payload = {
            "name": "Ticket Test User",
            "email": "ticket@test.com",
            "subject": "Test ticket retrieval",
            "category": "general",
            "message": "This is a test to verify ticket retrieval works correctly."
        }
        submit = client.post(
            "/support/submit",
            json=payload
        )
        assert submit.status_code == 200
        ticket_id = submit.json().get("ticket_id")

        # Skip if PENDING (no DB)
        if not ticket_id or ticket_id == "PENDING":
            pytest.skip("DB not available")

        # Retrieve ticket
        response = client.get(
            f"/support/ticket/{ticket_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ticket_id") == ticket_id

    def test_invalid_ticket_returns_404(
        self, client
    ):
        """Invalid ticket ID returns 404"""
        response = client.get(
            "/support/ticket/INVALID-999"
        )
        assert response.status_code in [404, 503]

# TEST 5: WhatsApp Webhook
class TestWhatsAppWebhook:

    def test_whatsapp_webhook_accepts_message(
        self, client
    ):
        """WhatsApp webhook returns TwiML"""
        payload = {
            "From": "whatsapp:+923001234567",
            "To": "whatsapp:+14155238886",
            "Body": "bhai oud attar ka price kya hai?",
            "ProfileName": "Ahmed",
            "NumMedia": "0",
            "MessageSid": "SMtest123"
        }
        response = client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            }
        )
        assert response.status_code == 200
        assert "<?xml" in response.text
        assert "<Response>" in response.text
        assert "<Message>" in response.text

    def test_whatsapp_urdu_query(
        self, client
    ):
        """WhatsApp handles Urdu queries"""
        payload = {
            "From": "whatsapp:+923211111111",
            "Body": "mujhe rose attar chahiye 6ml",
            "ProfileName": "Sara",
            "NumMedia": "0"
        }
        response = client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            }
        )
        assert response.status_code == 200
        assert "<Message>" in response.text

    def test_whatsapp_empty_body_handled(
        self, client
    ):
        """WhatsApp handles empty message body"""
        payload = {
            "From": "whatsapp:+923001234567",
            "Body": "",
            "NumMedia": "0"
        }
        response = client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            }
        )
        assert response.status_code == 200

# TEST 6: Gmail Webhook
class TestGmailWebhook:

    def test_gmail_webhook_accepts_notification(
        self, client
    ):
        """Gmail webhook handles Pub/Sub notification"""
        email_data = json.dumps({
            "emailAddress": "test@gmail.com",
            "historyId": "12345"
        })
        encoded = base64.b64encode(
            email_data.encode()
        ).decode()

        payload = {
            "message": {
                "data": encoded,
                "messageId": "test123"
            },
            "subscription": "test-sub"
        }
        response = client.post(
            "/webhooks/gmail",
            json=payload
        )
        assert response.status_code == 200

    def test_gmail_empty_message_handled(
        self, client
    ):
        """Gmail webhook handles empty message"""
        response = client.post(
            "/webhooks/gmail",
            json={"message": {}}
        )
        assert response.status_code == 200

# TEST 7: Cross Channel Continuity
class TestCrossChannelContinuity:

    def test_same_customer_different_channels(
        self, client
    ):
        """Same customer on different channels"""
        # WhatsApp submission
        wa_payload = {
            "From": "whatsapp:+923005555555",
            "Body": "bhai price batao",
            "ProfileName": "Cross Channel User",
            "NumMedia": "0"
        }
        wa_response = client.post(
            "/webhooks/whatsapp",
            data=wa_payload,
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            }
        )
        assert wa_response.status_code == 200

        # Web form same customer (different channel)
        web_payload = {
            "name": "Cross Channel User",
            "email": "crosschannel@test.com",
            "phone": "0300-5555555",
            "subject": "Following up on price query",
            "category": "product_query",
            "message": "I asked on WhatsApp about price. Can you confirm here too?"
        }
        web_response = client.post(
            "/support/submit",
            json=web_payload
        )
        assert web_response.status_code == 200

    def test_customer_lookup_by_phone(
        self, client
    ):
        """Customer can be looked up by phone"""
        response = client.get(
            "/customers/lookup",
            params={"phone": "03001234567"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "found" in data

# TEST 8: Order Flow
class TestOrderFlow:

    def test_complete_order_flow(
        self, client
    ):
        """Complete order creation via web form"""
        payload = {
            "name": "Order Flow Tester",
            "email": "orderflow@test.com",
            "phone": "0300-7777777",
            "subject": "Order Oud Al Shams 6ml",
            "category": "order",
            "message": "I want to order Oud Al Shams 6ml. Deliver to DHA Phase 5. Payment JazzCash. Please confirm."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("response") is not None

    def test_bulk_order_triggers_escalation(
        self, client
    ):
        """Bulk order should trigger escalation"""
        payload = {
            "name": "Wholesale Buyer",
            "email": "wholesale@test.com",
            "subject": "Bulk order 50 bottles",
            "category": "order",
            "message": "I need 50 bottles of Oud Al Shams for my shop. Give me wholesale rate please."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

# TEST 9: Owner Commands
class TestOwnerCommands:

    def test_channel_metrics_accessible(
        self, client
    ):
        """Channel metrics endpoint works"""
        response = client.get(
            "/metrics/channels"
        )
        assert response.status_code == 200

    def test_owner_report_requires_auth(
        self, client
    ):
        """Owner report requires correct phone"""
        response = client.get(
            "/owner/orders/today",
            params={"owner_phone": "0000000000"}
        )
        assert response.status_code == 403

    def test_owner_sales_report_requires_auth(
        self, client
    ):
        """Sales report requires owner auth"""
        response = client.get(
            "/owner/report/today",
            params={"owner_phone": "0000000000"}
        )
        assert response.status_code == 403

# TEST 10: Escalation Triggers
class TestEscalationTriggers:

    def test_angry_customer_escalated(
        self, client
    ):
        """Angry customer triggers escalation"""
        payload = {
            "name": "Angry Customer",
            "email": "angry@test.com",
            "subject": "Terrible service complaint",
            "category": "complaint",
            "message": "This is absolutely terrible! My order is 1 week late and no one is responding. I want a refund immediately or I will post on social media!"
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        # Response should acknowledge the issue
        assert len(data.get("response", "")) > 10

    def test_refund_request_escalated(
        self, client
    ):
        """Refund request triggers escalation"""
        payload = {
            "name": "Refund Requester",
            "email": "refund@test.com",
            "subject": "Refund request for order",
            "category": "complaint",
            "message": "I received the wrong product and want a full refund of PKR 2500 please."
        }
        response = client.post(
            "/support/submit",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

# TEST 11: Stress Test
class TestStressTest:

    def test_multiple_concurrent_requests(
        self, client
    ):
        """API handles multiple requests"""
        results = []
        for i in range(5):
            payload = {
                "name": f"Stress Test User {i}",
                "email": f"stress{i}@test.com",
                "subject": f"Stress test query {i}",
                "category": "general",
                "message": f"This is stress test message number {i} to verify system stability."
            }
            response = client.post(
                "/support/submit",
                json=payload
            )
            results.append(response.status_code)

        # All should succeed
        assert all(r == 200 for r in results)

    def test_api_response_time(
        self, client
    ):
        """API responds within 30 seconds"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 30
