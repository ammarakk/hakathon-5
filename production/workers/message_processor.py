# production/workers/message_processor.py

import os
import json
import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

TOPICS_TO_CONSUME = [
    "fte.tickets.incoming"
]

# Worker State
running = True

def handle_shutdown(signum, frame):
    global running
    print("\nShutdown signal received...")
    running = False

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# Process Single Message
async def process_ticket(
    payload: dict,
    db,
    kafka_producer
) -> bool:
    try:
        channel = payload.get("channel", "webform")
        customer_name = payload.get(
            "customer_name", "Customer"
        )
        identifier = payload.get("identifier", "")
        message = payload.get("message", "")
        metadata = payload.get("metadata", {})

        if not message or not identifier:
            print(f"Invalid payload: {payload}")
            return False

        print(
            f"Processing {channel} from "
            f"{customer_name}: {message[:50]}..."
        )

        from production.agent.customer_success_agent import (
            process_customer_message
        )

        start_time = datetime.now()

        response = await process_customer_message(
            message=message,
            channel=channel,
            customer_name=customer_name,
            identifier=identifier,
            db=db
        )

        processing_ms = int(
            (datetime.now() - start_time
             ).total_seconds() * 1000
        )

        print(
            f"Response ({processing_ms}ms): "
            f"{response.response[:80]}..."
        )

        # Send WhatsApp reply via Twilio
        if (channel == "whatsapp"
                and identifier):
            try:
                from production.channels.whatsapp_handler import (
                    send_whatsapp_message,
                    format_whatsapp_response
                )
                formatted = format_whatsapp_response(
                    response.response,
                    response.should_escalate
                )
                await send_whatsapp_message(
                    identifier,
                    formatted
                )
                print("WhatsApp reply sent")
            except Exception as e:
                print(f"WhatsApp send error: {e}")

        # Handle escalation
        if response.should_escalate:
            print(
                f"Escalating: "
                f"{response.escalation_reason}"
            )
            if kafka_producer:
                await kafka_producer.send(
                    "fte.escalations",
                    {
                        "channel": channel,
                        "customer": customer_name,
                        "identifier": identifier,
                        "reason": response.escalation_reason,
                        "timestamp": datetime.now().isoformat()
                    }
                )

            try:
                from production.channels.whatsapp_handler import (
                    notify_owner_escalation
                )
                await notify_owner_escalation(
                    customer_name,
                    identifier,
                    response.escalation_reason
                )
            except Exception as e:
                print(f"Owner notify error: {e}")

        # Send metrics
        if kafka_producer:
            await kafka_producer.send_metric(
                metric_type="ticket_processed",
                channel=channel,
                data={
                    "intent": response.detected_intent,
                    "escalated": response.should_escalate,
                    "sentiment": response.sentiment,
                    "processing_ms": processing_ms
                }
            )

        return True

    except Exception as e:
        print(f"Process ticket error: {e}")
        return False

# Send to DLQ
async def send_to_dlq(
    payload: dict,
    error: str,
    kafka_producer
):
    try:
        if kafka_producer:
            await kafka_producer.send(
                "fte.dlq",
                {
                    "original_topic": "fte.tickets.incoming",
                    "payload": payload,
                    "error": error,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"Sent to DLQ: {error[:50]}")
    except Exception as e:
        print(f"DLQ error: {e}")

# Main Worker Loop
async def run_worker():
    global running

    print("Starting Nur Scents Message Worker...")
    print(f"Kafka: {KAFKA_BOOTSTRAP}")
    print(f"Topics: {TOPICS_TO_CONSUME}\n")

    # Connect DB
    db = None
    try:
        from production.database.db import get_pool
        db = await get_pool()
        print("Database connected")
    except Exception as e:
        print(f"DB warning: {e}")

    # Connect Kafka Producer
    kafka_prod = None
    try:
        from production.kafka_client import (
            kafka_producer
        )
        kafka_prod = kafka_producer
        print("Kafka producer ready")
    except Exception as e:
        print(f"Kafka producer warning: {e}")

    # Start Consumer
    try:
        from kafka import KafkaConsumer

        consumer = KafkaConsumer(
            *TOPICS_TO_CONSUME,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="nur-scents-worker-group",
            auto_offset_reset="latest",
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            value_deserializer=lambda m:
                json.loads(m.decode('utf-8')),
            consumer_timeout_ms=1000
        )

        print(
            "Worker running - "
            "waiting for messages...\n"
        )
        print("Press Ctrl+C to stop\n")

        while running:
            try:
                for msg in consumer:
                    if not running:
                        break

                    payload = msg.value
                    topic = msg.topic

                    print(
                        f"\n{'='*50}\n"
                        f"Message from: {topic}\n"
                        f"Offset: {msg.offset}"
                    )

                    try:
                        success = await process_ticket(
                            payload, db, kafka_prod
                        )
                        if not success:
                            await send_to_dlq(
                                payload,
                                "Processing failed",
                                kafka_prod
                            )
                    except Exception as e:
                        print(f"Worker error: {e}")
                        await send_to_dlq(
                            payload,
                            str(e),
                            kafka_prod
                        )

            except Exception as e:
                if running:
                    print(f"Consumer loop error: {e}")
                    print("Reconnecting in 5s...")
                    await asyncio.sleep(5)

        consumer.close()
        print("Consumer closed.")

    except Exception as e:
        print(f"Kafka consumer error: {e}")
        print(
            "Running without Kafka...\n"
            "Messages via FastAPI only."
        )

        # Keep running without Kafka
        while running:
            await asyncio.sleep(1)

    finally:
        if db:
            await db.close()
        print("Worker shutdown complete.")

# Worker Health Check
async def worker_health_check():
    checks = {
        "kafka": False,
        "database": False,
        "agent": False
    }

    # Check Kafka
    try:
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            consumer_timeout_ms=3000
        )
        consumer.close()
        checks["kafka"] = True
    except Exception:
        pass

    # Check DB
    try:
        from production.database.db import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        checks["database"] = True
    except Exception:
        pass

    # Check Agent
    try:
        from production.agent.customer_success_agent import (
            get_model
        )
        get_model()
        checks["agent"] = True
    except Exception:
        pass

    print("\nWorker Health Check:")
    for service, status in checks.items():
        icon = "OK" if status else "FAIL"
        print(f"  {icon} {service}")

    return all(checks.values())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "health":
        asyncio.run(worker_health_check())
    else:
        asyncio.run(run_worker())
