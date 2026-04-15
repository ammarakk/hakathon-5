# production/kafka_client.py

import os
import json
import asyncio
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

# ─── Topics ──────────────────────────────────────
TOPICS = {
    "TICKETS": "fte.tickets.incoming",
    "WHATSAPP": "fte.channels.whatsapp.inbound",
    "EMAIL": "fte.channels.email.inbound",
    "WEBFORM": "fte.channels.webform.inbound",
    "ESCALATIONS": "fte.escalations",
    "METRICS": "fte.metrics",
    "DLQ": "fte.dlq"
}

# ─── Producer ────────────────────────────────────
class KafkaProducerClient:
    def __init__(self):
        self._producer = None

    async def get_producer(self):
        if not self._producer:
            try:
                from kafka import KafkaProducer
                self._producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP,
                    value_serializer=lambda v:
                        json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k:
                        k.encode('utf-8') if k else None,
                    retries=3,
                    acks='all'
                )
            except Exception as e:
                print(f"Kafka producer error: {e}")
                return None
        return self._producer

    async def send(
        self,
        topic: str,
        value: dict,
        key: str = None
    ) -> bool:
        try:
            producer = await self.get_producer()
            if not producer:
                print(f"Kafka unavailable — skipping: {topic}")
                return False

            future = producer.send(
                topic,
                value=value,
                key=key
            )
            producer.flush(timeout=10)
            return True
        except Exception as e:
            print(f"Kafka send error: {e}")
            await self.send_to_dlq(topic, value, str(e))
            return False

    async def send_to_dlq(
        self,
        original_topic: str,
        value: dict,
        error: str
    ):
        try:
            producer = await self.get_producer()
            if producer:
                producer.send(
                    TOPICS["DLQ"],
                    value={
                        "original_topic": original_topic,
                        "payload": value,
                        "error": error,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                producer.flush(timeout=5)
        except Exception as e:
            print(f"DLQ error: {e}")

    async def send_ticket(
        self,
        channel: str,
        customer_name: str,
        identifier: str,
        message: str,
        metadata: dict = None
    ) -> bool:
        payload = {
            "channel": channel,
            "customer_name": customer_name,
            "identifier": identifier,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "event_type": "new_ticket"
        }

        channel_topic = {
            "whatsapp": TOPICS["WHATSAPP"],
            "email": TOPICS["EMAIL"],
            "webform": TOPICS["WEBFORM"]
        }.get(channel, TOPICS["TICKETS"])

        await self.send(
            channel_topic, payload, key=identifier
        )
        return await self.send(
            TOPICS["TICKETS"], payload, key=identifier
        )

    async def send_metric(
        self,
        metric_type: str,
        channel: str,
        data: dict
    ) -> bool:
        payload = {
            "metric_type": metric_type,
            "channel": channel,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return await self.send(
            TOPICS["METRICS"], payload
        )

    def close(self):
        if self._producer:
            self._producer.close()
            self._producer = None

kafka_producer = KafkaProducerClient()
