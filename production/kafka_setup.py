# production/kafka_setup.py

import os
import time
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

TOPICS = [
    {
        "name": "fte.tickets.incoming",
        "partitions": 3,
        "replication": 1,
        "description": "All incoming tickets"
    },
    {
        "name": "fte.channels.whatsapp.inbound",
        "partitions": 2,
        "replication": 1,
        "description": "WhatsApp messages"
    },
    {
        "name": "fte.channels.email.inbound",
        "partitions": 2,
        "replication": 1,
        "description": "Email messages"
    },
    {
        "name": "fte.channels.webform.inbound",
        "partitions": 2,
        "replication": 1,
        "description": "Web form submissions"
    },
    {
        "name": "fte.escalations",
        "partitions": 1,
        "replication": 1,
        "description": "Escalation events"
    },
    {
        "name": "fte.metrics",
        "partitions": 1,
        "replication": 1,
        "description": "Performance metrics"
    },
    {
        "name": "fte.dlq",
        "partitions": 1,
        "replication": 1,
        "description": "Dead letter queue"
    }
]

def create_topics():
    try:
        from kafka.admin import (
            KafkaAdminClient,
            NewTopic
        )
        from kafka.errors import (
            TopicAlreadyExistsError
        )

        print(f"Connecting to Kafka: {KAFKA_BOOTSTRAP}")

        admin = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            client_id="nur-scents-admin"
        )

        new_topics = []
        for topic in TOPICS:
            new_topics.append(NewTopic(
                name=topic["name"],
                num_partitions=topic["partitions"],
                replication_factor=topic["replication"]
            ))

        try:
            admin.create_topics(new_topics)
            print("Topics created:")
            for t in TOPICS:
                print(f"  OK {t['name']}")
        except TopicAlreadyExistsError:
            print("Topics already exist - OK")

        existing = admin.list_topics()
        print(f"\nAll topics: {len(existing)}")
        for t in existing:
            if t.startswith("fte."):
                print(f"  TOPIC {t}")

        admin.close()
        return True

    except Exception as e:
        print(f"Kafka setup error: {e}")
        print("Kafka may not be ready yet")
        print("Try: cd infrastructure/docker && docker-compose up -d kafka")
        return False

def test_producer_consumer():
    try:
        from kafka import KafkaProducer, KafkaConsumer
        import json

        print("\nTesting producer...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v:
                json.dumps(v).encode('utf-8')
        )

        test_msg = {
            "test": True,
            "channel": "whatsapp",
            "message": "test message",
            "timestamp": str(time.time())
        }

        producer.send(
            "fte.tickets.incoming",
            value=test_msg
        )
        producer.flush()
        print("OK Producer test passed")
        producer.close()

        print("\nTesting consumer...")
        consumer = KafkaConsumer(
            "fte.tickets.incoming",
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset='latest',
            consumer_timeout_ms=3000,
            value_deserializer=lambda m:
                json.loads(m.decode('utf-8'))
        )

        print("OK Consumer connected")
        consumer.close()

        print("\nOK Kafka fully working!")
        return True

    except Exception as e:
        print(f"Kafka test error: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Kafka topics...\n")

    # Retry up to 3 times
    for attempt in range(3):
        if create_topics():
            break
        print(f"Retry {attempt + 1}/3...")
        time.sleep(5)

    test_producer_consumer()
