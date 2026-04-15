# debug/full_system_test.py
import httpx
import json

BASE = "http://localhost:8000"

def test(name, fn):
    try:
        result = fn()
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
        return result
    except Exception as e:
        print(f"[FAIL] {name}: {str(e)[:60]}")
        return False

def check_health():
    r = httpx.get(f"{BASE}/health", timeout=10)
    data = r.json()
    print(f"   DB: {data['services']['database']}")
    print(f"   Kafka: {data['services']['kafka']}")
    print(f"   Agent: {data['services']['agent']}")
    return r.status_code == 200

def check_web_form():
    r = httpx.post(
        f"{BASE}/support/submit",
        json={
            "name": "Test Ahmed",
            "email": "test@test.com",
            "phone": "0300-1234567",
            "subject": "Oud attar price test",
            "category": "product_query",
            "message": "bhai oud attar ka price batao"
        },
        timeout=30
    )
    data = r.json()
    has_response = bool(data.get("response"))
    if has_response:
        print(f"   AI Response: {data['response'][:80]}...")
    else:
        print(f"   ❌ No AI response!")
        print(f"   Full data: {data}")
    return r.status_code == 200 and has_response

def check_whatsapp():
    r = httpx.post(
        f"{BASE}/webhooks/whatsapp",
        data={
            "From": "whatsapp:+923001234567",
            "Body": "bhai oud price?",
            "ProfileName": "Test",
            "NumMedia": "0"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=30
    )
    has_xml = "<?xml" in r.text
    if has_xml:
        import re
        msg = re.search(r'<Message>(.*?)</Message>', r.text, re.DOTALL)
        if msg:
            print(f"   WA Reply: {msg.group(1)[:80]}...")
    return r.status_code == 200 and has_xml

def check_metrics():
    r = httpx.get(f"{BASE}/metrics/channels", timeout=10)
    return r.status_code == 200

print("="*50)
print("Nur Scents Full System Test")
print("="*50)
print()

results = {
    "Health Check": test("Health Check", check_health),
    "Web Form + AI": test("Web Form + AI Response", check_web_form),
    "WhatsApp Webhook": test("WhatsApp Webhook", check_whatsapp),
    "Channel Metrics": test("Channel Metrics", check_metrics),
}

print()
print("="*50)
passed = sum(results.values())
total = len(results)
print(f"Results: {passed}/{total} passing")
print("="*50)

if passed == total:
    print("\n[SUCCESS] SYSTEM FULLY WORKING!")
    print("Ready for hackathon demo!")
else:
    failed = [k for k,v in results.items() if not v]
    print(f"\n[FAIL] Fix these: {', '.join(failed)}")
