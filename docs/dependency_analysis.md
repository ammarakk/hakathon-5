# Dependency Analysis - Nur Scents Customer Success Agent

## Python Backend Dependencies

### Core Framework
```python
fastapi==0.115.0          # Modern, fast web framework for building APIs
uvicorn[standard]==0.32.0 # ASGI server for running FastAPI
pydantic==2.9.2           # Data validation using Python type annotations
pydantic-settings==2.6.0  # Settings management using Pydantic
python-multipart==0.0.12  # Multipart form data support
python-dotenv==1.0.1      # Read environment variables from .env file
```

**How They Work Together:**
```
FastAPI (Web Framework)
    ↓
Pydantic (Validation)
    ↓
Uvicorn (ASGI Server)
    ↓
Client Requests
```

**Usage Example:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

class Product(BaseModel):
    id: str
    name: str
    price: float

app = FastAPI()

@app.post("/products")
async def create_product(product: Product):
    # FastAPI validates with Pydantic automatically
    return {"success": True, "product": product}
```

### Database Layer
```python
psycopg[binary]==3.2.3        # PostgreSQL database adapter
psycopg2-binary==2.9.9        # Alternative PostgreSQL adapter
sqlalchemy==2.0.35            # SQL toolkit and ORM
alembic==1.13.3               # Database migration tool
asyncpg==0.29.0               # Async PostgreSQL driver for FastAPI
```

**Architecture:**
```
FastAPI Endpoints
    ↓
SQLAlchemy ORM (Models)
    ↓
asyncpg (Async Driver)
    ↓
PostgreSQL Database
    ↓
pgvector Extension (Vector Search)
```

**Usage Example:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Product

# Async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db"
)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Usage in endpoint
@app.get("/products/{product_id}")
async def get_product(product_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        return product
```

### Vector Database (pgvector)
```python
pgvector==0.3.4  # PostgreSQL vector extension for similarity search
```

**Purpose:** Enable semantic search for FAQ matching

**Usage Example:**
```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text

class FAQ(Base):
    __tablename__ = 'knowledge_base'

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension

# Similarity search
@app.post("/faq/search")
async def search_faq(query: str):
    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Find similar FAQs
    similar = await session.execute(
        select(FAQ)
        .order_by(FAQ.embedding.cosine_distance(query_embedding))
        .limit(5)
    )
    return similar.scalars().all()
```

### Kafka Streaming
```python
confluent-kafka==2.5.3  # Apache Kafka client with high performance
kafka-python==2.0.2     # Alternative Python Kafka client
```

**Architecture:**
```
Webhook receives message
    ↓
Publish to Kafka Topic
    ↓
Consumer Group Processes
    ↓
AI Agent generates response
    ↓
Publish response topic
    ↓
Response Worker sends message
```

**Usage Example:**
```python
from confluent_kafka import Producer, Consumer

# Producer (Webhook)
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery_report(err, msg):
    if err is not None:
        print(f'Message failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}')

# Publish event
producer.produce(
    'whatsapp.events',
    key='customer_phone',
    value=json.dumps(message),
    callback=delivery_report
)
producer.flush()

# Consumer (Message Worker)
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'nur_scents_agent_group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['whatsapp.events'])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    event = json.loads(msg.value())
    # Process with AI agent
    response = process_with_agent(event)
    consumer.commit()
```

### AI Agent Framework
```python
pydantic-ai==0.0.14              # AI agent framework with Pydantic integration
google-generativeai==0.8.3       # Google Gemini API client
google-api-core==2.22.0          # Core Google API libraries
google-auth==2.35.0              # Google authentication
```

**PydanticAI Architecture:**
```
PydanticAI Agent
    ↓
Tool Definitions (Functions)
    ↓
Gemini 2.0 Flash (LLM)
    ↓
Response Generation
```

**Usage Example:**
```python
from pydantic_ai import Agent
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
llm = GenerativeModel(settings.GEMINI_MODEL)

# Define tools for agent
def search_products(query: str) -> list[Product]:
    """Search products by query"""
    # Query database
    return products

def get_order_status(order_number: str) -> Order:
    """Get order status"""
    # Query database
    return order

# Create agent
agent = Agent(
    name="nur_assistant",
    model=llm,
    tools=[search_products, get_order_status],
    instructions=(
        "You are Nur Assistant, a helpful customer service agent "
        "for Nur Scents perfume brand in Karachi, Pakistan. "
        "Respond in Roman Urdu for WhatsApp, formal English for email."
    )
)

# Use agent
response = agent.run(
    "Oudh ki price kya hai?",
    context={"channel": "whatsapp"}
)
print(response.content)  # "Oudh Royale PKR 12,500 hai..."
```

### Twilio WhatsApp Integration
```python
twilio==9.3.1  # Twilio API client for WhatsApp messaging
```

**Architecture:**
```
Customer WhatsApp
    ↓
Twilio API
    ↓
Webhook to FastAPI
    ↓
AI Agent Processing
    ↓
Twilio API (Send Message)
    ↓
Customer WhatsApp
```

**Usage Example:**
```python
from twilio.rest import Client

# Initialize Twilio client
client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)

# Send WhatsApp message
def send_whatsapp_message(to_number: str, message: str):
    message = client.messages.create(
        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
        body=message,
        to=f"whatsapp:{to_number}"
    )
    return message.sid

# Receive webhook (in FastAPI endpoint)
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    message_body = form_data.get("Body")
    from_number = form_data.get("From").replace("whatsapp:", "")

    # Process with AI
    response = agent.run(message_body)
    send_whatsapp_message(from_number, response.content)
```

### Gmail API Integration
```python
google-api-python-client==2.149.0  # Google API client library
google-auth-httplib2==0.2.0        # HTTP transport for Google Auth
google-auth-oauthlib==1.2.1        # OAuth 2.0 for Google
email-validator==2.1.1             # Email validation
```

**Architecture:**
```
Gmail API
    ↓
OAuth 2.0 Authentication
    ↓
Watch for Push Notifications
    ↓
Webhook to FastAPI
    ↓
Fetch Email Content
    ↓
AI Agent Processing
    ↓
Send Reply via Gmail API
```

**Usage Example:**
```python
import google.auth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

# Initialize Gmail service
def get_gmail_service():
    credentials = Credentials.from_authorized_user_file(
        'token.json',
        ['https://www.googleapis.com/auth/gmail.modify']
    )
    service = build('gmail', 'v1', credentials=credentials)
    return service

# Fetch email
def fetch_email(message_id: str):
    service = get_gmail_service()
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    # Parse headers
    headers = message['payload']['headers']
    subject = next(h['value'] for h in headers if h['name'] == 'Subject')
    from_email = next(h['value'] for h in headers if h['name'] == 'From')

    # Parse body
    body = base64.urlsafe_b64decode(
        message['payload']['body']['data']
    ).decode('utf-8')

    return {
        'from': from_email,
        'subject': subject,
        'body': body
    }

# Send email
def send_email(to: str, subject: str, body: str):
    service = get_gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
```

### Async & Utilities
```python
httpx==0.27.2              # Async HTTP client
aiofiles==24.1.0           # Async file operations
tenacity==9.0.0            # Retry logic with exponential backoff
pytz==2024.2               # Timezone support
python-dateutil==2.9.0     # Date parsing utilities
```

**Usage Example:**
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import pytz
from datetime import datetime

# Async HTTP client
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_product_catalog():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.nurscents.pk/products",
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

# Timezone handling
def get_karachi_time():
    tz = pytz.timezone('Asia/Karachi')
    return datetime.now(tz)

# Async file operations
import aiofiles

async def write_log(message: str):
    async with aiofiles.open('app.log', mode='a') as f:
        await f.write(f'{message}\n')
```

### Security
```python
passlib[bcrypt]==1.7.4           # Password hashing
python-jose[cryptography]==3.3.0 # JWT token handling
cryptography==44.0.0             # Cryptographic recipes
```

**Usage Example:**
```python
from passlib.context import CryptContext
from jose import jwt, JWTError

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None
```

### Logging & Monitoring
```python
loguru==0.7.2                # Advanced logging
prometheus-client==0.21.0    # Prometheus metrics
```

**Usage Example:**
```python
from loguru import logger
from prometheus_client import Counter, Histogram

# Configure logging
logger.add(
    "app.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)

# Use logging
logger.info("Order created", extra={"order_id": order_number})
logger.error("Payment failed", exc_info=True)

# Metrics
order_counter = Counter(
    'orders_created_total',
    'Total orders created',
    ['payment_method']
)

order_duration = Histogram(
    'order_processing_seconds',
    'Time spent processing orders'
)

# Use metrics
order_counter.labels(payment_method='cod').inc()
order_duration.observe(processing_time)
```

## Frontend Dependencies

### Core Framework
```json
{
  "next": "14.2.15",           // React framework with app router
  "react": "^18.3.1",          // UI library
  "react-dom": "^18.3.1"       // React DOM renderer
}
```

**How They Work Together:**
```
Next.js App Router
    ↓
React Components
    ↓
React DOM (Browser)
```

### Styling
```json
{
  "tailwindcss": "^3.4.14",        // Utility-first CSS framework
  "autoprefixer": "^10.4.20",      // Add vendor prefixes
  "postcss": "^8.4.47",            // CSS transformation
  "@tailwindcss/forms": "^0.5.9",  // Form styling
  "@tailwindcss/typography": "^0.5.15" // Prose styling
}
```

**Custom Configuration:**
```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { /* Pink tones */ },
        gold: { /* Gold tones */ },
        wood: { /* Wood tones */ }
      }
    }
  }
}
```

### Data Fetching & State
```json
{
  "axios": "^1.7.7",        // HTTP client
  "swr": "^2.2.5",          // Data fetching with caching
  "zustand": "^5.0.1"       // State management
}
```

**Usage Example:**
```typescript
// SWR for data fetching
import useSWR from 'swr';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

function ProductsList() {
  const { data, error, isLoading } = useSWR(
    '/api/v1/products',
    fetcher
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading products</div>;

  return data.products.map(product => (
    <ProductCard key={product.id} product={product} />
  ));
}

// Zustand for global state
import { create } from 'zustand';

const useCartStore = create((set) => ({
  cart: [],
  addItem: (item) => set((state) => ({
    cart: [...state.cart, item]
  }))
}));
```

### Forms & Validation
```json
{
  "react-hook-form": "^7.53.2",   // Form management
  "zod": "^3.23.8",                // Schema validation
  "@hookform/resolvers": "^3.9.1"  // Zod integration
}
```

**Usage Example:**
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const supportSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  message: z.string().min(10)
});

type SupportFormData = z.infer<typeof supportSchema>;

function SupportForm() {
  const { register, handleSubmit, formState: { errors } } =
    useForm<SupportFormData>({
      resolver: zodResolver(supportSchema)
    });

  const onSubmit = async (data: SupportFormData) => {
    await axios.post('/api/v1/webhook/web-support', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}

      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <textarea {...register('message')} />
      {errors.message && <span>{errors.message.message}</span>}

      <button type="submit">Submit</button>
    </form>
  );
}
```

### UI Components
```json
{
  "lucide-react": "^0.454.0",        // Icon library
  "react-hot-toast": "^2.4.1",       // Toast notifications
  "framer-motion": "^11.11.17"       // Animation library
}
```

**Usage Example:**
```typescript
import { ShoppingCart, Phone } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

function ProductCard({ product }) {
  const addToCart = () => {
    toast.success('Added to cart!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <ShoppingCart />
      <Phone />
      <button onClick={addToCart}>Add to Cart</button>
    </motion.div>
  );
}
```

### Utilities
```json
{
  "clsx": "^2.1.1",               // Conditional class names
  "tailwind-merge": "^2.5.4",     // Merge Tailwind classes
  "date-fns": "^4.1.0"            // Date formatting
}
```

**Usage Example:**
```typescript
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format } from 'date-fns';

// Utility function for merging classes
function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// Usage
<button className={cn(
  'px-4 py-2',
  isActive && 'bg-primary-500',
  isLoading && 'opacity-50'
)}>

// Date formatting
const formatted = format(new Date(), 'PPpp'); // "Apr 9, 2026, 10:30 PM"
```

## Dependency Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                       │
│  React → SWR → Axios → FastAPI Backend                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  Pydantic Validation → Business Logic → Response            │
└─────┬─────────────┬──────────────┬──────────────┬──────────┘
      │             │              │              │
      ▼             ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │  Kafka   │  │ Gemini   │  │ Twilio   │
│+pgvector │  │          │  │  AI      │  │          │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Key Integration Points

1. **Frontend → Backend**: HTTP REST API (Axios)
2. **Backend → Database**: Async PostgreSQL (asyncpg)
3. **Backend → Kafka**: Event streaming (confluent-kafka)
4. **Backend → AI**: Gemini API (google-generativeai)
5. **Backend → WhatsApp**: Twilio API
6. **Backend → Email**: Gmail API
7. **Kafka → Workers**: Event consumers (confluent-kafka)

This dependency architecture provides a robust, scalable foundation for the Nur Scents Customer Success Agent.
