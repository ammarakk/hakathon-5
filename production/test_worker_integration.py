# production/test_worker_integration.py

"""
Test script for Kafka + Worker integration
Run this after Docker Desktop is restarted
"""

import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime

print("=" * 60)
print("Nur Scents FTE - Kafka Worker Integration Test")
print("=" * 60)

print("\nStep 1: Check Docker Desktop Status")
print("-" * 60)

try:
    result = subprocess.run(
        ["docker", "ps"],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        print("OK Docker Desktop is running")
        docker_ok = True
    else:
        print("FAIL Docker Desktop has issues")
        print(f"Error: {result.stderr}")
        docker_ok = False

except Exception as e:
    print(f"FAIL Docker error: {e}")
    print("\nTO FIX: Restart Docker Desktop on Windows")
    print("1. Close Docker Desktop")
    print("2. Wait 10 seconds")
    print("3. Open Docker Desktop")
    print("4. Wait for 'Docker Desktop is running'")
    print("5. Run this test again")
    docker_ok = False

    sys.exit(1)

if docker_ok:
    print("\nStep 2: Check Docker Compose Services")
    print("-" * 60)

    os.chdir("infrastructure/docker")
    result = subprocess.run(
        ["docker-compose", "ps"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    print("\nStep 3: Start Kafka if not running")
    print("-" * 60)

    subprocess.run(
        ["docker-compose", "up", "-d", "kafka"],
        capture_output=True
    )

    print("Waiting 30 seconds for Kafka to be ready...")
    time.sleep(30)

    print("\nStep 4: Test Kafka Setup")
    print("-" * 60)

    os.chdir("../..")
    result = subprocess.run(
        ["python", "production/kafka_setup.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"Errors: {result.stderr}")

    print("\nStep 5: Worker Health Check")
    print("-" * 60)

    result = subprocess.run(
        ["python", "production/workers/message_processor.py", "health"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"Errors: {result.stderr}")

    print("\nStep 6: Test Full Pipeline")
    print("-" * 60)
    print("This test requires:")
    print("1. FastAPI running on port 8000")
    print("2. Worker running in separate terminal")
    print("3. Kafka running")
    print("\nTo test manually:")
    print("Terminal 1: cd infrastructure/docker && docker-compose up -d")
    print("Terminal 2: uvicorn production.api.main:app --reload")
    print("Terminal 3: python production/workers/message_processor.py")
    print("Terminal 4: curl -X POST http://localhost:8000/support/submit \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name":"Sara Ahmed","email":"sara@gmail.com",')
    print('"phone":"0321-9876543","subject":"Rose attar price",')
    print('"category":"product_query",')
    print('"message":"Mujhe rose attar ka price batao"}\'')

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
