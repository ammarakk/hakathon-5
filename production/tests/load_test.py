# production/tests/load_test.py

import random
import json
from locust import HttpUser, task, between, events
from datetime import datetime

# Test Data
PAKISTANI_NAMES = [
    "Ahmed Khan", "Sara Ali", "Bilal Hassan",
    "Zara Ahmed", "Tariq Mahmood", "Ayesha Malik",
    "Usman Siddiqui", "Fatima Nawaz", "Ali Raza",
    "Sana Sheikh", "Hassan Mirza", "Hira Baig",
    "Imran Qureshi", "Nadia Iqbal", "Faisal Butt"
]

KARACHI_AREAS = [
    "DHA Phase 5", "Clifton Block 4",
    "Gulshan-e-Iqbal Block 13",
    "PECHS Block 2", "Saddar Town",
    "North Karachi Sector 11",
    "Korangi Industrial Area",
    "Malir Halt", "FB Area Block 15",
    "Bahria Town Precinct 12"
]

PRODUCTS = [
    "Oud Al Shams 6ml",
    "Sultan Oud 12ml",
    "Gulab Sitara 6ml",
    "Rose Oud Blend 3ml",
    "White Musk Body Mist 50ml",
    "Nur Classic Set",
    "Royal Oud Gift Box"
]

PAYMENT_METHODS = [
    "JazzCash", "EasyPaisa",
    "Bank Transfer", "COD"
]

PRODUCT_QUERIES_URDU = [
    "bhai oud attar ka price kya hai?",
    "kya rose attar available hai?",
    "gift set ka price batao",
    "mujhe 6ml attar chahiye",
    "kya DHA mein deliver karte ho?",
    "white musk spray kitne ka hai?",
    "bulk order pe discount milta hai?",
    "konsa attar best hai mardana?",
    "ladies ke liye kya recommend karo ge?",
    "cash on delivery available hai?"
]

PRODUCT_QUERIES_ENGLISH = [
    "What are the prices for oud attar?",
    "Do you have gift sets available?",
    "Is delivery available in Clifton?",
    "What payment methods do you accept?",
    "Can I get a refund if not satisfied?",
    "How long does delivery take to DHA?",
    "Do you offer wholesale pricing?",
    "What is your return policy?",
    "Are there any discounts available?",
    "Do you ship outside Karachi?"
]

COMPLAINTS = [
    "My order hasn't arrived after 3 days",
    "I received the wrong product",
    "The package was damaged on delivery",
    "I was charged wrong amount",
    "Product quality is not as described"
]

# Web Form User
class WebFormUser(HttpUser):
    """Simulate web form submissions"""
    wait_time = between(2, 8)
    weight = 3

    @task(5)
    def submit_product_query(self):
        """Most common - product query"""
        name = random.choice(PAKISTANI_NAMES)
        payload = {
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}{random.randint(1,999)}@gmail.com",
            "phone": f"030{random.randint(10000000, 99999999)}",
            "subject": random.choice(PRODUCT_QUERIES_ENGLISH),
            "category": "product_query",
            "message": (
                random.choice(PRODUCT_QUERIES_ENGLISH) +
                " Please provide details and pricing."
            )
        }
        with self.client.post(
            "/support/submit",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(3)
    def submit_order_request(self):
        """Order placement via web form"""
        name = random.choice(PAKISTANI_NAMES)
        product = random.choice(PRODUCTS)
        area = random.choice(KARACHI_AREAS)
        payment = random.choice(PAYMENT_METHODS)

        payload = {
            "name": name,
            "email": f"order{random.randint(1,9999)}@test.com",
            "phone": f"032{random.randint(10000000, 99999999)}",
            "subject": f"Order: {product}",
            "category": "order",
            "message": (
                f"I want to order {product}. "
                f"Deliver to {area}. "
                f"Payment via {payment}. "
                f"Please confirm availability."
            )
        }
        with self.client.post(
            "/support/submit",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(2)
    def submit_tracking_request(self):
        """Order tracking via web form"""
        payload = {
            "name": random.choice(PAKISTANI_NAMES),
            "email": f"track{random.randint(1,999)}@test.com",
            "subject": "Track my order",
            "category": "tracking",
            "message": (
                f"I placed an order 2 days ago. "
                f"My phone is 030{random.randint(10000000,99999999)}. "
                f"Please update me on status."
            )
        }
        with self.client.post(
            "/support/submit",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def submit_complaint(self):
        """Complaint submission"""
        payload = {
            "name": random.choice(PAKISTANI_NAMES),
            "email": f"complaint{random.randint(1,999)}@test.com",
            "subject": "Complaint about order",
            "category": "complaint",
            "message": random.choice(COMPLAINTS) +
                " Please resolve this urgently."
        }
        with self.client.post(
            "/support/submit",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

# WhatsApp Simulation User
class WhatsAppSimUser(HttpUser):
    """Simulate WhatsApp messages via webhook"""
    wait_time = between(3, 10)
    weight = 2

    @task(4)
    def send_product_query_urdu(self):
        """WhatsApp Urdu product query"""
        payload = {
            "From": f"whatsapp:+9230{random.randint(10000000,99999999)}",
            "To": "whatsapp:+14155238886",
            "Body": random.choice(PRODUCT_QUERIES_URDU),
            "ProfileName": random.choice(PAKISTANI_NAMES),
            "NumMedia": "0",
            "MessageSid": f"SM{random.randint(100000,999999)}"
        }
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            catch_response=True
        ) as response:
            if (response.status_code == 200 and "<?xml" in response.text):
                response.success()
            else:
                response.failure(f"Bad response: {response.status_code}")

    @task(3)
    def send_order_via_whatsapp(self):
        """WhatsApp order placement"""
        product = random.choice(PRODUCTS)
        area = random.choice(KARACHI_AREAS)
        payment = random.choice(["JazzCash", "EasyPaisa"])
        payload = {
            "From": f"whatsapp:+9232{random.randint(10000000,99999999)}",
            "Body": (
                f"mujhe {product} chahiye. "
                f"{area} deliver karna. "
                f"{payment} karunga."
            ),
            "ProfileName": random.choice(PAKISTANI_NAMES),
            "NumMedia": "0"
        }
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(2)
    def send_tracking_query(self):
        """WhatsApp tracking request"""
        payload = {
            "From": f"whatsapp:+9233{random.randint(10000000,99999999)}",
            "Body": "mera order kab ayega? 2 din ho gaye",
            "ProfileName": random.choice(PAKISTANI_NAMES),
            "NumMedia": "0"
        }
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

# Health Check User
class HealthCheckUser(HttpUser):
    """Monitor system health during test"""
    wait_time = between(5, 15)
    weight = 1

    @task(3)
    def check_health(self):
        """Regular health check"""
        with self.client.get(
            "/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health degraded")
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def check_metrics(self):
        """Check channel metrics"""
        with self.client.get(
            "/metrics/channels",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics failed: {response.status_code}")

    @task(1)
    def check_docs(self):
        """Verify API docs accessible"""
        with self.client.get(
            "/docs",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Docs failed: {response.status_code}")

# Event Listeners
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*50)
    print("Nur Scents Load Test Starting")
    print(f"Target: http://localhost:8000")
    print("="*50 + "\n")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats
    total = stats.total

    print("\n" + "="*50)
    print("Load Test Results")
    print("="*50)
    print(f"Total Requests: {total.num_requests}")
    print(f"Failures: {total.num_failures}")
    print(f"Failure Rate: {total.fail_ratio:.1%}")
    print(f"Avg Response: {total.avg_response_time:.0f}ms")
    print(f"P95 Response: {total.get_response_time_percentile(0.95):.0f}ms")
    print(f"RPS: {total.current_rps:.1f}")

    # Check targets
    p95 = total.get_response_time_percentile(0.95)
    fail_rate = total.fail_ratio

    print("\nTarget Results:")
    print(f"  P95 < 3000ms: {'OK' if p95 < 3000 else 'FAIL'} ({p95:.0f}ms)")
    print(f"  Failure < 1%: {'OK' if fail_rate < 0.01 else 'FAIL'} ({fail_rate:.1%})")
    print(f"  Uptime > 99%: {'OK' if fail_rate < 0.01 else 'FAIL'}")
    print("="*50 + "\n")
