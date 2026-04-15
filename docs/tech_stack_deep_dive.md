# Tech Stack Deep Dive - Implementation Guide

## PydanticAI + Gemini 2.0 Flash

### Understanding PydanticAI

PydanticAI is a modern Python agent framework that combines:
- **Type Safety**: Pydantic models for structured data
- **Tool Calling**: Define functions the agent can use
- **Streaming**: Real-time response generation
- **Multi-modal**: Text, images, audio support

### Implementation Structure

```python
# backend/app/services/agent_service.py

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List, Optional
import json

# Define models for structured outputs
class ProductSearchResult(BaseModel):
    """Structured output for product searches"""
    products: List[dict]
    total_count: int
    search_query: str

class OrderConfirmation(BaseModel):
    """Structured output for order confirmation"""
    order_number: str
    estimated_delivery: str
    total_amount: float
    payment_method: str

# Define tools that the agent can use
async def search_products_tool(
    query: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None
) -> ProductSearchResult:
    """Search for products based on query"""
    # Query database
    from app.services.product_service import ProductService
    service = ProductService()

    products = await service.search_products(
        query=query,
        category=category,
        max_price=max_price
    )

    return ProductSearchResult(
        products=[p.dict() for p in products],
        total_count=len(products),
        search_query=query
    )

async def get_product_details_tool(product_id: str) -> dict:
    """Get detailed information about a product"""
    from app.services.product_service import ProductService
    service = ProductService()

    product = await service.get_product(product_id)
    return product.dict() if product else None

async def create_order_tool(
    customer_phone: str,
    products: List[dict],
    address: str,
    city: str,
    payment_method: str
) -> OrderConfirmation:
    """Create a new order"""
    from app.services.order_service import OrderService
    service = OrderService()

    order = await service.create_order(
        customer_phone=customer_phone,
        products=products,
        address=address,
        city=city,
        payment_method=payment_method
    )

    return OrderConfirmation(
        order_number=order.order_number,
        estimated_delivery=order.estimated_delivery,
        total_amount=order.total_amount,
        payment_method=order.payment_method
    )

async def get_order_status_tool(order_number: str) -> dict:
    """Get the current status of an order"""
    from app.services.order_service import OrderService
    service = OrderService()

    order = await service.get_order_by_number(order_number)
    return {
        "order_number": order.order_number,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "estimated_delivery": order.estimated_delivery
    }

async def check_stock_tool(product_id: str, quantity: int = 1) -> dict:
    """Check if products are in stock"""
    from app.services.product_service import ProductService
    service = ProductService()

    product = await service.get_product(product_id)
    in_stock = product.stock >= quantity

    return {
        "product_id": product_id,
        "product_name": product.name,
        "requested_quantity": quantity,
        "available_stock": product.stock,
        "in_stock": in_stock,
        "can_fulfill": in_stock
    }

# Create the agent
def create_nur_scents_agent():
    """Create and configure the Nur Scents AI agent"""

    agent = Agent(
        name="nur_assistant",
        model="gemini-2.0-flash-exp",
        tools=[
            search_products_tool,
            get_product_details_tool,
            create_order_tool,
            get_order_status_tool,
            check_stock_tool
        ],
        instructions="""You are Nur Assistant, a helpful and polite customer service agent for Nur Scents.

BUSINESS CONTEXT:
- Nur Scents is a premium attar and fragrance brand based in Karachi, Pakistan
- Owner: Ammar
- We sell high-quality attars, oudh, musk, and oriental fragrances
- All prices are in PKR (Pakistani Rupees)
- We deliver to Karachi, Lahore, Islamabad, Rawalpindi
- Free delivery above PKR 15,000

RESPONSE GUIDELINES BY CHANNEL:

WhatsApp (Roman Urdu):
- Friendly, informal tone
- Use Roman Urdu (e.g., "Oudh ki price PKR 12,500 hai")
- Use emojis: 🌸 💐 ✨
- Greeting: "Assalam o Alaikum! 👋"
- Closing: "Allah Hafiz! 🌸"

Email (Formal English):
- Professional, polite tone
- Use formal English
- No emojis
- Greeting: "Dear Customer,"
- Closing: "Best regards, Nur Scents Team"

Web (Mixed):
- Semi-formal tone
- Can mix English and Roman Urdu
- Some emojis allowed
- Greeting: "Hello! Welcome to Nur Scents."
- Closing: "Thank you for choosing Nur Scents! 💐"

CAPABILITIES:
- Search products by name, category, or price range
- Provide detailed product information
- Create orders and calculate totals
- Check order status
- Answer questions about delivery, returns, refunds
- Make product recommendations

ESCALATION RULES:
- Escalate to owner if customer mentions: refund, complaint, legal, police
- Escalate if issue not resolved after 1 reply
- Owner identified by phone number in system

CULTURAL SENSITIVITY:
- Use Islamic greetings appropriately
- Be respectful and patient
- Avoid: alcohol, pig, haram references
- Frame as "attar/perfume" not "alcohol-based"

PRODUCT KNOWLEDGE:
- Oudh: Premium, expensive, long-lasting
- Musk: Clean, daily wear, affordable
- Floral: Rose, jasmine, lily - feminine
- Oriental: Amber, saffron - warm, rich
- Bakhoor: Traditional, for home
- Bundles: Gift sets, best value

When helping customers, be helpful and guide them to the best products for their needs."""
    )

    return agent

# Main agent service
class AgentService:
    """Service for interacting with the AI agent"""

    def __init__(self):
        self.agent = create_nur_scents_agent()

    async def process_message(
        self,
        message: str,
        channel: str = "web",
        customer_context: Optional[dict] = None
    ) -> str:
        """Process a customer message through the agent"""

        # Adjust instructions based on channel
        channel_context = self._get_channel_context(channel)

        # Run agent
        result = await self.agent.run(
            message,
            context={
                "channel": channel,
                "customer": customer_context or {},
                **channel_context
            }
        )

        return result.content

    def _get_channel_context(self, channel: str) -> dict:
        """Get channel-specific context"""

        contexts = {
            "whatsapp": {
                "language": "Roman Urdu",
                "tone": "friendly, informal",
                "emojis": True,
                "greeting": "Assalam o Alaikum! 👋"
            },
            "email": {
                "language": "Formal English",
                "tone": "professional, polite",
                "emojis": False,
                "greeting": "Dear Customer,"
            },
            "web": {
                "language": "Mixed",
                "tone": "semi-formal",
                "emojis": True,
                "greeting": "Hello! Welcome to Nur Scents."
            }
        }

        return contexts.get(channel, contexts["web"])

    async def should_escalate(
        self,
        message: str,
        conversation_history: List[dict]
    ) -> tuple[bool, str]:
        """Determine if conversation should be escalated to owner"""

        urgent_keywords = [
            "refund", "complaint", "fraud", "cheat", "scam",
            "police", "legal", "court", "lawyer"
        ]

        message_lower = message.lower()

        # Check for urgent keywords
        for keyword in urgent_keywords:
            if keyword in message_lower:
                return True, f"Urgent keyword detected: {keyword}"

        # Check if too many AI replies without resolution
        ai_replies = sum(1 for msg in conversation_history if msg.get("ai_generated"))
        if ai_replies >= 1:
            return True, "Issue not resolved after 1 AI reply"

        # Check if owner is explicitly mentioned
        if "owner" in message_lower or "ammar" in message_lower:
            return True, "Customer requested to speak with owner"

        return False, ""

# Usage in endpoint
@app.post("/api/v1/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    message = form_data.get("Body")
    from_number = form_data.get("From")

    # Get customer context
    customer = await get_customer_by_phone(from_number)

    # Process with agent
    agent_service = AgentService()
    response = await agent_service.process_message(
        message=message,
        channel="whatsapp",
        customer_context=customer.dict() if customer else None
    )

    # Check escalation
    conversation_history = await get_conversation_history(from_number)
    should_escalate, reason = await agent_service.should_escalate(
        message,
        conversation_history
    )

    if should_escalate:
        # Notify owner
        await notify_owner(from_number, message, reason)
        response = "Main Ammar (owner) se baat karwa raha hun. Thori der mein woh contact karenge. JazakAllah!"

    # Send response via Twilio
    send_whatsapp_message(from_number, response)

    return {"success": True}
```

## Kafka Message Workers

### Producer Implementation

```python
# backend/app/services/kafka_producer.py

from confluent_kafka import Producer
import json
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KafkaProducer:
    """Kafka producer for publishing events"""

    def __init__(self):
        self.config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'nur-scents-producer',
            'acks': 'all',  # Wait for all replicas
            'retries': 3,
            'max.in.flight': 1,
            'enable.idempotence': True
        }
        self.producer = Producer(self.config)

    def delivery_report(self, err, msg):
        """Callback for message delivery"""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(
                f'Message delivered to {msg.topic()} '
                f'[{msg.partition()}] @ offset {msg.offset()}'
            )

    def publish_event(
        self,
        topic: str,
        event_data: Dict[str, Any],
        key: str = None
    ) -> None:
        """Publish event to Kafka topic"""

        try:
            # Serialize event
            value = json.dumps(event_data).encode('utf-8')

            # Publish
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8') if key else None,
                value=value,
                callback=self.delivery_report
            )

            # Flush to ensure delivery
            self.producer.flush(timeout=10)

        except Exception as e:
            logger.error(f'Failed to publish event: {e}')
            raise

    def publish_whatsapp_event(self, from_number: str, message: str) -> None:
        """Publish WhatsApp message event"""

        event = {
            'event_type': 'whatsapp_message',
            'channel': 'whatsapp',
            'from': from_number,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_WHATSAPP_EVENTS,
            event_data=event,
            key=from_number
        )

    def publish_email_event(
        self,
        from_email: str,
        subject: str,
        body: str
    ) -> None:
        """Publish email event"""

        event = {
            'event_type': 'email_received',
            'channel': 'email',
            'from': from_email,
            'subject': subject,
            'body': body,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_EMAIL_EVENTS,
            event_data=event,
            key=from_email
        )

    def publish_web_event(
        self,
        name: str,
        email: str,
        message: str
    ) -> None:
        """Publish web form event"""

        event = {
            'event_type': 'web_inquiry',
            'channel': 'web',
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.publish_event(
            topic=settings.KAFKA_TOPIC_WEB_EVENTS,
            event_data=event,
            key=email
        )

# Global producer instance
kafka_producer = KafkaProducer()
```

### Consumer Implementation

```python
# backend/app/services/kafka_consumer.py

from confluent_kafka import Consumer
import json
from typing import Callable
from app.core.config import settings
from app.services.agent_service import AgentService
import logging

logger = logging.getLogger(__name__)

class KafkaConsumer:
    """Kafka consumer for processing events"""

    def __init__(self, topics: list[str]):
        self.config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_GROUP_ID,
            'auto.offset.reset': settings.KAFKA_AUTO_OFFSET_RESET,
            'enable.auto.commit': True
        }
        self.consumer = Consumer(self.config)
        self.topics = topics
        self.agent_service = AgentService()

    def process_whatsapp_event(self, event: dict) -> None:
        """Process WhatsApp message event"""

        from_number = event['from']
        message = event['message']

        logger.info(f'Processing WhatsApp message from {from_number}')

        try:
            # Get customer context
            customer = await self.get_customer(from_number)

            # Process with AI agent
            response = await self.agent_service.process_message(
                message=message,
                channel='whatsapp',
                customer_context=customer
            )

            # Send response via Twilio
            await self.send_whatsapp_response(from_number, response)

            # Log conversation
            await self.save_conversation(
                customer_id=customer.id if customer else None,
                channel='whatsapp',
                message=message,
                response=response
            )

        except Exception as e:
            logger.error(f'Error processing WhatsApp event: {e}')

    def process_email_event(self, event: dict) -> None:
        """Process email event"""

        from_email = event['from']
        subject = event['subject']
        body = event['body']

        logger.info(f'Processing email from {from_email}')

        try:
            # Get customer context
            customer = await self.get_customer(from_email)

            # Process with AI agent
            response = await self.agent_service.process_message(
                message=f"{subject}\n\n{body}",
                channel='email',
                customer_context=customer
            )

            # Send email response
            await self.send_email_response(from_email, response)

            # Log conversation
            await self.save_conversation(
                customer_id=customer.id if customer else None,
                channel='email',
                message=f"{subject}\n\n{body}",
                response=response
            )

        except Exception as e:
            logger.error(f'Error processing email event: {e}')

    def process_web_event(self, event: dict) -> None:
        """Process web form event"""

        name = event['name']
        email = event['email']
        message = event['message']

        logger.info(f'Processing web inquiry from {email}')

        try:
            # Get customer context
            customer = await self.get_customer(email)

            # Process with AI agent
            response = await self.agent_service.process_message(
                message=message,
                channel='web',
                customer_context={'name': name, **customer}
            )

            # Send email response
            await self.send_email_response(email, response)

            # Log conversation
            await self.save_conversation(
                customer_id=customer.id if customer else None,
                channel='web',
                message=message,
                response=response
            )

        except Exception as e:
            logger.error(f'Error processing web event: {e}')

    def start_consuming(self):
        """Start consuming messages from Kafka"""

        self.consumer.subscribe(self.topics)
        logger.info(f'Started consuming from topics: {self.topics}')

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    logger.error(f'Consumer error: {msg.error()}')
                    continue

                # Parse event
                event = json.loads(msg.value().decode('utf-8'))
                event_type = event.get('event_type')
                channel = event.get('channel')

                logger.info(
                    f'Received {event_type} from {msg.topic()} '
                    f'[{msg.partition()} @ offset {msg.offset()}]'
                )

                # Route to appropriate handler
                if channel == 'whatsapp':
                    await self.process_whatsapp_event(event)
                elif channel == 'email':
                    await self.process_email_event(event)
                elif channel == 'web':
                    await self.process_web_event(event)

                # Commit offset
                self.consumer.commit(msg)

        except KeyboardInterrupt:
            logger.info('Stopping consumer...')
        finally:
            self.consumer.close()

# Start consumer for all channels
def start_message_worker():
    """Start the Kafka message worker"""

    topics = [
        settings.KAFKA_TOPIC_WHATSAPP_EVENTS,
        settings.KAFKA_TOPIC_EMAIL_EVENTS,
        settings.KAFKA_TOPIC_WEB_EVENTS
    ]

    consumer = KafkaConsumer(topics)
    consumer.start_consuming()

if __name__ == '__main__':
    start_message_worker()
```

### Running the Worker

```bash
# Run as separate process
python -m app.services.kafka_consumer
```

## Twilio WhatsApp Integration

### Complete Implementation

```python
# backend/app/services/whatsapp_service.py

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for WhatsApp messaging via Twilio"""

    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_message(
        self,
        to_number: str,
        message: str,
        media_url: str = None
    ) -> str:
        """Send WhatsApp message"""

        try:
            # Ensure number is in correct format
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Send message
            message_obj = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message,
                to=to_number,
                media_url=media_url
            )

            logger.info(
                f'WhatsApp message sent: {message_obj.sid} '
                f'to {to_number}'
            )

            return message_obj.sid

        except Exception as e:
            logger.error(f'Failed to send WhatsApp message: {e}')
            raise

    def send_order_confirmation(
        self,
        to_number: str,
        order_number: str,
        total_amount: float
    ) -> str:
        """Send order confirmation message"""

        message = f"""✅ Order Confirmed!

Order Number: {order_number}
Total Amount: PKR {total_amount:,.2f}

Your order has been placed successfully!
We'll process it soon and send tracking details.

JazakAllah! 🌸"""

        return self.send_message(to_number, message)

    def send_order_status_update(
        self,
        to_number: str,
        order_number: str,
        status: str
    ) -> str:
        """Send order status update"""

        status_messages = {
            'confirmed': '📦 Confirmed! Processing your order.',
            'processing': '🔧 Preparing your order for shipment.',
            'shipped': '🚚 Shipped! Track your package.',
            'delivered': '✅ Delivered! Enjoy your fragrance.'
        }

        message = f"""Order Update: {order_number}
{status_messages.get(status, 'Status updated')}

Thank you for choosing Nur Scents! 💐"""

        return self.send_message(to_number, message)

    def parse_incoming_message(self, form_data: dict) -> dict:
        """Parse incoming webhook data"""

        return {
            'message_sid': form_data.get('MessageSid'),
            'from_number': form_data.get('From', '').replace('whatsapp:', ''),
            'to_number': form_data.get('To', '').replace('whatsapp:', ''),
            'body': form_data.get('Body', ''),
            'num_media': int(form_data.get('NumMedia', 0)),
            'media_urls': [
                form_data.get(f'MediaUrl{i}')
                for i in range(int(form_data.get('NumMedia', 0)))
            ],
            'timestamp': form_data.get('Timestamp', '')
        }

# Global service instance
whatsapp_service = WhatsAppService()
```

## Gmail API Integration

### OAuth Setup & Email Handling

```python
# backend/app/services/email_service.py

import google.auth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email
from email.mime.text import MIMEText
from typing import List, Dict
from app.core.config import settings
import logging
import os
import pickle

logger = logging.getLogger(__name__)

class GmailService:
    """Service for Gmail API integration"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self):
        self.creds_path = settings.GMAIL_CREDENTIALS_PATH
        self.token_path = settings.GMAIL_TOKEN_PATH
        self.service = None

    def authenticate(self) -> None:
        """Authenticate with Gmail API"""

        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path,
                self.SCOPES
            )

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_email(self, message_id: str) -> Dict:
        """Fetch email by message ID"""

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Parse headers
            headers = message['payload']['headers']

            def get_header(name):
                return next(
                    (h['value'] for h in headers if h['name'] == name),
                    None
                )

            # Parse body
            body = self._get_email_body(message['payload'])

            return {
                'message_id': message_id,
                'from': get_header('From'),
                'to': get_header('To'),
                'subject': get_header('Subject'),
                'date': get_header('Date'),
                'body': body,
                'thread_id': message.get('threadId')
            }

        except Exception as e:
            logger.error(f'Failed to fetch email: {e}')
            raise

    def _get_email_body(self, payload: dict) -> str:
        """Extract email body from payload"""

        body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                body += self._get_email_body(part)
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')

        return body

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None
    ) -> str:
        """Send email"""

        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_params = {
                'userId': 'me',
                'body': {'raw': raw}
            }

            if thread_id:
                send_params['body']['threadId'] = thread_id

            result = self.service.users().messages().send(**send_params).execute()

            logger.info(f'Email sent: {result["id"]} to {to}')

            return result['id']

        except Exception as e:
            logger.error(f'Failed to send email: {e}')
            raise

    def watch_inbox(self) -> str:
        """Set up Gmail push notifications"""

        try:
            request = {
                'labelIds': ['INBOX'],
                'topicName': f'projects/{settings.GCP_PROJECT_ID}/topics/gmail'
            }

            result = self.service.users().watch(
                userId='me',
                body=request
            ).execute()

            logger.info(f'Gmail watch set up: {result.get("historyId")}')

            return result.get('historyId')

        except Exception as e:
            logger.error(f'Failed to watch inbox: {e}')
            raise

    def get_unread_messages(self) -> List[Dict]:
        """Get list of unread messages"""

        try:
            result = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD']
            ).execute()

            messages = result.get('messages', [])

            unread_emails = []
            for msg in messages[:10]:  # Limit to 10
                email_data = self.fetch_email(msg['id'])
                unread_emails.append(email_data)

            return unread_emails

        except Exception as e:
            logger.error(f'Failed to get unread messages: {e}')
            raise

# Global service instance
gmail_service = GmailService()
```

## Next.js Frontend Implementation

### Support Form Component

```typescript
// frontend/app/components/SupportForm.tsx

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast, { Toaster } from 'react-hot-toast';
import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

// Validation schema
const supportSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  message: z.string().min(10, 'Message must be at least 10 characters'),
  inquiryType: z.string().optional()
});

type SupportFormData = z.infer<typeof supportSchema>;

export default function SupportForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportSchema)
  });

  const onSubmit = async (data: SupportFormData) => {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/v1/webhook/web-support', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (result.success) {
        toast.success('Support request received! We\'ll get back to you soon.');
        reset();
      } else {
        toast.error('Failed to submit. Please try again.');
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Toaster position="top-center" />

      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-gold-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-serif text-wood-800 mb-2">
              How Can We Help?
            </h1>
            <p className="text-wood-600">
              Send us a message and we\'ll respond as soon as possible
            </p>
          </div>

          {/* Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-wood-700 mb-2">
                  Name *
                </label>
                <input
                  {...register('name')}
                  type="text"
                  className="w-full px-4 py-3 border border-wood-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Your name"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.name.message}
                  </p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-wood-700 mb-2">
                  Email *
                </label>
                <input
                  {...register('email')}
                  type="email"
                  className="w-full px-4 py-3 border border-wood-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="your@email.com"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-wood-700 mb-2">
                  Phone Number (Optional)
                </label>
                <input
                  {...register('phone')}
                  type="tel"
                  className="w-full px-4 py-3 border border-wood-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="+92 XXX XXXXXXX"
                />
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-wood-700 mb-2">
                  Message *
                </label>
                <textarea
                  {...register('message')}
                  rows={5}
                  className="w-full px-4 py-3 border border-wood-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Tell us what you need help with..."
                />
                {errors.message && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.message.message}
                  </p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-primary-600 text-white py-4 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Send Message
                  </>
                )}
              </button>

            </form>
          </div>

          {/* Contact Info */}
          <div className="mt-8 text-center text-sm text-wood-600">
            <p>Or reach us directly:</p>
            <p className="mt-2">
              <span className="font-semibold">WhatsApp:</span> +92 XXX XXXXXXX
            </p>
            <p className="mt-1">
              <span className="font-semibold">Email:</span> contact@nurscents.pk
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
```

This deep dive provides implementation guidance for all major components. Each service is designed to be modular, testable, and production-ready.
