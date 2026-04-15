# Nur Scents Customer Success Agent - Architecture Analysis

## System Overview

The Nur Scents Customer Success Agent is a **multi-channel AI-powered customer support system** that handles WhatsApp, Email, and Web inquiries through a unified streaming architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CUSTOMER CHANNELS                        │
├──────────────┬──────────────┬───────────────────────────────────┤
│  WhatsApp    │     Email    │         Web Support Form          │
│  (Twilio)    │  (Gmail API) │         (Next.js)                 │
└──────┬───────┴──────┬───────┴───────────────┬───────────────────┘
       │              │                       │
       │              │                       │
       ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KAFKA EVENT STREAM                           │
│  whatsapp.events  │  email.events  │  web.events  │  agent.events│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MESSAGE WORKER (Python)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PydanticAI Agent + Gemini 2.0 Flash                      │  │
│  │  - Route message to appropriate handler                   │  │
│  │  - Generate contextual response                           │  │
│  │  - Query database for customer/product info               │  │
│  │  - Determine if escalation needed                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              POSTGRESQL + PGVECTOR DATABASE                     │
│  customers │ products │ orders │ conversations │ knowledge_base │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESPONSE CHANNELS                           │
│  WhatsApp Response │ Email Response │ Web Notification          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Analysis

### 1. Frontend (Next.js 14)
**Purpose:** Customer-facing web interface and support form

**Key Components:**
- **App Router:** Next.js 14 app directory structure
- **Tailwind CSS:** Custom color scheme (primary pink, gold, wood tones)
- **Support Form:** Multi-language input (Roman Urdu + English)
- **Product Catalog:** Display real Nur Scents products
- **Order Tracking:** Customer self-service portal

**Dependencies:**
- `next@14.2.15` - React framework
- `react@18.3.1` - UI library
- `tailwindcss@3.4.14` - Styling
- `axios` - HTTP client for API calls
- `swr` - Data fetching and caching
- `react-hook-form` - Form validation
- `zod` - Schema validation

**Integration Points:**
```typescript
// API calls to backend
const API_URL = process.env.NEXT_PUBLIC_API_URL; // http://localhost:8000

// Support form submission
POST /api/v1/webhook/web-support
{
  "name": "Customer Name",
  "email": "customer@example.com",
  "message": "Inquiry message"
}

// Product catalog fetch
GET /api/v1/products
GET /api/v1/products/{product_id}
```

### 2. Backend (FastAPI)
**Purpose:** Core API server, message processing, and business logic

**Directory Structure:**
```
backend/app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Settings and environment variables
│   └── logging.py         # Loguru logging configuration
├── api/
│   ├── endpoints/
│   │   ├── health.py      # Health check endpoints
│   │   ├── products.py    # Product catalog endpoints
│   │   ├── orders.py      # Order management endpoints
│   │   └── webhook.py     # Channel webhook endpoints
│   └── __init__.py        # API router aggregation
├── models/                # SQLAlchemy ORM models (TODO)
├── services/              # Business logic services (TODO)
└── utils/                 # Helper utilities (TODO)
```

**Current Endpoints:**
```
GET  /health              # Health check
GET  /                    # Root endpoint
GET  /api/v1/products     # Get all products (with filters)
GET  /api/v1/products/{id} # Get specific product
POST /api/v1/orders       # Create new order
GET  /api/v1/orders/{number} # Get order details
POST /api/v1/webhook/whatsapp       # WhatsApp webhook
POST /api/v1/webhook/web-support    # Web support form
POST /api/v1/webhook/email/gmail    # Gmail webhook
GET  /api/v1/webhook/whatsapp/verify # Webhook verification
```

**Dependencies:**
- `fastapi@0.115.0` - Web framework
- `uvicorn` - ASGI server
- `pydantic@2.9.2` - Data validation
- `sqlalchemy@2.0.35` - ORM
- `asyncpg@0.29.0` - Async PostgreSQL driver
- `confluent-kafka@2.5.3` - Kafka client
- `pydantic-ai@0.0.14` - AI agent framework
- `google-generativeai@0.8.3` - Gemini API
- `twilio@9.3.1` - WhatsApp integration
- `loguru@0.7.2` - Logging

### 3. Database (PostgreSQL + pgvector)
**Purpose:** Persistent storage for customers, products, orders, conversations

**Schema Overview:**
```sql
customers        # Customer profiles and preferences
products         # Nur Scents product catalog
orders           # Order records and tracking
order_items      # Line items for each order
conversations    # All customer interactions across channels
knowledge_base   # FAQ with vector embeddings
incidents        # Escalated issues requiring human intervention
daily_reports    # Automated daily summary reports
email_queue      # Outbound email queue
```

**Key Features:**
- **pgvector extension:** Vector similarity search for FAQ matching
- **Indexes:** Performance optimization on frequently queried fields
- **Triggers:** Automatic timestamp updates
- **JSONB columns:** Flexible metadata storage
- **Foreign keys:** Referential integrity

**Connection String:**
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/nur_scents_db"
```

### 4. Streaming (Kafka)
**Purpose:** Event-driven communication between channels and agent

**Topics:**
```yaml
whatsapp.events:     # Incoming WhatsApp messages
email.events:        # Incoming emails
web.events:          # Web form submissions
orders.events:       # Order lifecycle events
agent.events:        # Agent responses
escalations.events:  # Escalation to owner
```

**Event Flow:**
```
1. Channel webhook receives message
2. Publish to corresponding topic (whatsapp.events)
3. Message worker consumes event
4. Process with PydanticAI agent
5. Publish response to agent.events
6. Response worker sends back through channel
```

**Kafka Configuration:**
```python
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_GROUP_ID = "nur_scents_agent_group"
KAFKA_AUTO_OFFSET_RESET = "earliest"
```

### 5. AI Agent (PydanticAI + Gemini 2.0 Flash)
**Purpose:** Understand customer queries and generate contextual responses

**Agent Capabilities:**
- Product recommendations based on preferences
- Order taking and validation
- Status inquiry handling
- FAQ answering (with vector similarity search)
- Escalation detection
- Multi-language response generation (Roman Urdu, English)

**Configuration:**
```python
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 1024
```

**Response Rules by Channel:**
```json
{
  "whatsapp": {
    "language": "Roman Urdu",
    "tone": "friendly, informal",
    "emojis": true,
    "greeting": "Assalam o Alaikum! 👋"
  },
  "email": {
    "language": "Formal English",
    "tone": "professional, polite",
    "emojis": false,
    "greeting": "Dear Customer,"
  },
  "web": {
    "language": "Mixed (English + Roman Urdu)",
    "tone": "semi-formal",
    "emojis": true,
    "greeting": "Hello! Welcome to Nur Scents."
  }
}
```

## Data Flow Analysis

### Customer Inquiry Flow

```
1. CUSTOMER SENDS MESSAGE
   ├─ WhatsApp: "Oudh ki price kya hai?"
   ├─ Email: "What is the price of Oudh?"
   └─ Web Form: "Oudh price?"

2. WEBHOOK RECEIVES
   ├─ Twilio sends to /api/v1/webhook/whatsapp
   ├─ Gmail sends to /api/v1/webhook/email/gmail
   └─ Next.js posts to /api/v1/webhook/web-support

3. PUBLISH TO KAFKA
   ├─ whatsapp.events: {"from": "+92...", "message": "...", "timestamp": "..."}
   ├─ email.events: {"from": "email@example.com", "subject": "...", "body": "..."}
   └─ web.events: {"name": "...", "email": "...", "message": "..."}

4. MESSAGE WORKER CONSUMES
   ├─ Parse message
   ├─ Identify customer (look up by phone/email)
   ├─ Extract intent (product inquiry, order, complaint)
   └─ Gather context (previous conversations, customer history)

5. PYDANTIC AI AGENT PROCESSES
   ├─ Determine response type
   ├─ Query database if needed (product info, order status)
   ├─ Generate contextual response
   └─ Check if escalation needed

6. RESPONSE GENERATED
   ├─ WhatsApp: "Oudh Royale PKR 12,500 hai. Bestseller hai! 🌸"
   ├─ Email: "Dear Customer, The price of Oudh Royale is PKR 12,500..."
   └─ Web: "Oudh Royale is PKR 12,500. Bestseller! 💐"

7. SEND RESPONSE
   ├─ WhatsApp: Twilio API sendMessage
   ├─ Email: Gmail API send
   └─ Web: JSON response + email confirmation

8. LOG CONVERSATION
   ├─ Save to conversations table
   ├─ Update customer context
   └─ Generate analytics
```

### Order Flow

```
1. CUSTOMER PLACES ORDER
   "Main order karna chahta hoon:
    - Oudh Royale (12ml)
    - Musk Al Tahara (6ml)
    Address: [details]"

2. AI AGENT PROCESSES
   ├─ Parse products and quantities
   ├─ Calculate total (PKR 12,500 + 4,500 = PKR 17,000)
   ├─ Check stock availability
   ├─ Calculate delivery charges (free above 15,000)
   ├─ Confirm shipping details
   └─ Generate order confirmation

3. CREATE ORDER IN DATABASE
   ├─ Generate order number: NS-20260409223456
   ├─ Save order with status: "pending"
   ├─ Save line items
   ├─ Publish to orders.events topic
   └─ Send confirmation to customer

4. OWNER NOTIFICATION
   ├─ Email order details to Ammar
   ├─ WhatsApp notification (if urgent)
   └─ Update dashboard

5. ORDER PROCESSING
   ├─ Confirm payment
   ├─ Update status: "confirmed" → "processing" → "shipped"
   ├─ Send tracking updates to customer
   └─ Mark as "delivered"
```

## Integration Points

### Twilio WhatsApp Integration
**Webhook URL:** `https://your-domain.com/api/v1/webhook/whatsapp`

**Incoming Payload:**
```python
{
    "MessageSid": "SM...",
    "From": "whatsapp:+923001234567",
    "Body": "Oudh ki price kya hai?",
    "Timestamp": "2026-04-09T17:22:00Z"
}
```

**Outbound via Twilio API:**
```python
client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+923001234567",
    body="Oudh Royale PKR 12,500 hai. Bestseller hai! 🌸"
)
```

### Gmail API Integration
**Setup Required:**
1. Google Cloud Project
2. Gmail API enabled
3. OAuth 2.0 credentials (credentials.json)
4. Watch for push notifications

**Webhook Handler:**
```python
# Receive Gmail pub/sub notification
POST /api/v1/webhook/email/gmail
{
    "message": {
        "data": "<base64_encoded_message_id>",
        "messageId": "..."
    }
}

# Fetch email content
gmail_service.users().messages().get(
    userId='me',
    message_id=message_id,
    format='metadata',
    metadataHeaders=['From', 'Subject', 'To']
).execute()
```

### Frontend API Integration
**Axios Instance:**
```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});
```

**Support Form:**
```typescript
const submitSupportForm = async (data: SupportFormData) => {
  const response = await api.post('/api/v1/webhook/web-support', data);
  return response.data;
};
```

## Key Findings & Implementation Gaps

### ✅ What's Complete
1. Project structure and configuration
2. Database schema with all tables
3. Real Nur Scents product data
4. Backend API skeleton with endpoints
5. Frontend project setup
6. Docker Compose for infrastructure
7. Business rules and configuration

### 🔨 What Needs Implementation (Priority Order)

#### HIGH PRIORITY (Core Functionality)
1. **PydanticAI Agent Implementation**
   - Agent class with tool definitions
   - Product catalog query tool
   - Order creation tool
   - Order status lookup tool
   - Customer history lookup tool
   - Escalation detector

2. **Kafka Message Workers**
   - Consumer groups for each channel
   - Event processing logic
   - Error handling and retry
   - Dead letter queue

3. **Database Models & Services**
   - SQLAlchemy models
   - Async database session
   - CRUD operations
   - Vector similarity search for FAQ

4. **Twilio WhatsApp Integration**
   - Webhook message parsing
   - Outbound message sending
   - Media message handling
   - Message templates

5. **Gmail Email Integration**
   - OAuth flow setup
   - Email fetching
   - Email sending
   - Attachment handling

#### MEDIUM PRIORITY (Enhancement)
6. **Frontend Support Form**
   - Form UI with Tailwind
   - Multi-language input
   - Real-time validation
   - Submission tracking

7. **Customer Dashboard**
   - Order tracking
   - History view
   - Support ticket status

8. **Daily Report Generator**
   - Cron job/scheduled task
   - Analytics aggregation
   - Email generation
   - PDF generation

#### LOWER PRIORITY (Polish)
9. **k3s Kubernetes Deployment**
   - Container orchestration
   - Service mesh
   - Ingress configuration
   - Scaling policies

10. **Monitoring & Logging**
    - Prometheus metrics
    - Grafana dashboards
    - Centralized logging
    - Alert configuration

## Technical Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini API rate limits | High | Implement caching, queue management |
| Kafka message loss | High | Enable acknowledgments, persistence |
| Database connection pool exhaustion | Medium | Connection pooling, health checks |
| Twilio sandbox limitations | Medium | Plan for production upgrade |
| Gmail OAuth token expiry | Medium | Auto-refresh mechanism |
| Vector search accuracy | Medium | Fine-tune embeddings, fallback to keyword search |

## Next Steps for Implementation

Based on this analysis, the recommended implementation order is:

1. **Step 7:** Complete PostgreSQL Schema Implementation
2. **Step 8:** Build PydanticAI Agent with all tools
3. **Step 9:** Complete FastAPI Backend Services
4. **Step 12:** Set up Kafka and Message Workers
5. **Step 10:** Implement Twilio WhatsApp Handler
6. **Step 14:** Implement Gmail Email Handler
7. **Step 11:** Build Next.js Support Form
8. **Step 15:** Deploy to k3d Kubernetes
9. **Step 16-18:** Testing and Documentation

This architecture provides a solid foundation for a scalable, multi-channel AI customer support system.
