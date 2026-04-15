"""
Kafka producer and consumer services
"""

from confluent_kafka import Producer, Consumer, KafkaException
from typing import Dict, Any, Callable, Optional
import json
from datetime import datetime
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Kafka producer for publishing events"""

    def __init__(self):
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "nur-scents-producer",
            "acks": "all",
            "retries": 3,
            "max.in.flight": 1,
            "enable.idempotence": True,
        }
        self.producer = Producer(self.config)

    def delivery_report(self, err, msg):
        """Callback for message delivery confirmation"""
        if err is not None:
            logger.error(f"❌ Message delivery failed: {err}")
        else:
            logger.info(
                f"✅ Message delivered to {msg.topic()} "
                f"[{msg.partition()}] @ offset {msg.offset()}"
            )

    def publish_event(
        self, topic: str, event_data: Dict[str, Any], key: Optional[str] = None
    ) -> None:
        """
        Publish event to Kafka topic

        Args:
            topic: Kafka topic
            event_data: Event data
            key: Optional message key
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in event_data:
                event_data["timestamp"] = datetime.utcnow().isoformat()

            # Serialize event
            value = json.dumps(event_data).encode("utf-8")

            # Publish message
            self.producer.produce(
                topic=topic,
                key=key.encode("utf-8") if key else None,
                value=value,
                callback=self.delivery_report,
            )

            # Flush to ensure delivery
            self.producer.flush(timeout=10)

            logger.info(f"📤 Published event to {topic}")

        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            raise

    def publish_whatsapp_event(self, from_number: str, message: str) -> None:
        """Publish WhatsApp message event"""

        event = {
            "event_type": "whatsapp_message",
            "channel": "whatsapp",
            "from": from_number,
            "message": message,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_WHATSAPP_EVENTS, event_data=event, key=from_number
        )

    def publish_email_event(self, from_email: str, subject: str, body: str) -> None:
        """Publish email event"""

        event = {
            "event_type": "email_received",
            "channel": "email",
            "from": from_email,
            "subject": subject,
            "body": body,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_EMAIL_EVENTS, event_data=event, key=from_email
        )

    def publish_web_event(
        self, name: str, email: str, message: str, phone: Optional[str] = None
    ) -> None:
        """Publish web form event"""

        event = {
            "event_type": "web_inquiry",
            "channel": "web",
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_WEB_EVENTS, event_data=event, key=email
        )

    def publish_order_event(
        self, order_number: str, status: str, customer_data: Dict
    ) -> None:
        """Publish order event"""

        event = {
            "event_type": "order_update",
            "channel": "orders",
            "order_number": order_number,
            "status": status,
            "customer": customer_data,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_ORDER_EVENTS,
            event_data=event,
            key=order_number,
        )

    def publish_agent_event(
        self, channel: str, customer_id: str, response: str
    ) -> None:
        """Publish agent response event"""

        event = {
            "event_type": "agent_response",
            "channel": channel,
            "customer_id": customer_id,
            "response": response,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_AGENT_EVENTS, event_data=event, key=customer_id
        )

    def publish_escalation_event(
        self, channel: str, customer_id: str, reason: str, conversation_data: Dict
    ) -> None:
        """Publish escalation event"""

        event = {
            "event_type": "escalation",
            "channel": channel,
            "customer_id": customer_id,
            "reason": reason,
            "conversation": conversation_data,
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_ESCALATION_EVENTS,
            event_data=event,
            key=customer_id,
        )


class KafkaConsumer:
    """Kafka consumer for processing events"""

    def __init__(self, topics: list[str], group_id: str):
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": group_id,
            "auto.offset.reset": settings.KAFKA_AUTO_OFFSET_RESET,
            "enable.auto.commit": True,
        }
        self.topics = topics
        self.consumer = None
        self.running = False

    def start(self):
        """Start the consumer"""
        self.consumer = Consumer(self.config)
        self.consumer.subscribe(self.topics)
        self.running = True
        logger.info(f"🔄 Started Kafka consumer for topics: {self.topics}")

    def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("⏹️ Stopped Kafka consumer")

    def process_messages(self, handler: Callable[[Dict], None]):
        """
        Process messages from Kafka topics

        Args:
            handler: Callback function to handle each message
        """

        if not self.consumer:
            self.start()

        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"❌ Consumer error: {msg.error()}")
                    continue

                # Parse message
                try:
                    event = json.loads(msg.value().decode("utf-8"))
                    event_type = event.get("event_type")
                    channel = event.get("channel")

                    logger.info(
                        f"📥 Received {event_type} from {msg.topic()} "
                        f"[{msg.partition()} @ offset {msg.offset()}]"
                    )

                    # Call handler
                    handler(event)

                    # Commit offset
                    self.consumer.commit(msg)

                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("⏹️ Consumer interrupted")
        finally:
            self.stop()


# Global producer instance
kafka_producer = KafkaProducer()


def create_message_worker(topics: Optional[list[str]] = None) -> KafkaConsumer:
    """
    Create a message worker consumer

    Args:
        topics: List of topics to consume from

    Returns:
        KafkaConsumer instance
    """
    if topics is None:
        topics = [
            settings.KAFKA_TOPIC_WHATSAPP_EVENTS,
            settings.KAFKA_TOPIC_EMAIL_EVENTS,
            settings.KAFKA_TOPIC_WEB_EVENTS,
        ]

    return KafkaConsumer(
        topics=topics, group_id=settings.KAFKA_GROUP_ID + "_worker"
    )
