# Technical Specifications - Remaining Implementation

## Document Overview

**Purpose:** Detailed specifications for remaining components to complete the Nur Scents Customer Success Agent
**Status:** Phase 1 (Incubation) Complete → Phase 2 (Specialization) Ready
**Last Updated:** 2026-04-09

---

## Component 1: Twilio WhatsApp Integration

### Specification

**Priority:** HIGH (10 pts - Channel Integration)
**Step:** 10
**Dependencies:** FastAPI backend, agent service

### Technical Requirements

#### 1.1 Webhook Endpoint
**File:** `backend/app/api/endpoints/whatsapp.py`

**Endpoint:**
```
POST /api/v1/webhook/whatsapp
```

**Functionality:**
- Receive Twilio webhook POST requests
- Parse form-data (Twilio format)
- Extract: From, To, Body, MediaUrls, MessageSid
- Validate phone number format
- Handle media files (images, audio, video)
- Publish to Kafka topic: `whatsapp.events`
- Return 200 OK immediately (acknowledge receipt)

**Validation:**
```python
- From number must be WhatsApp format (+92...)
- Body must not be empty
- MessageSid must be unique
- Rate limiting: 10 messages/minute per number
```

**Error Handling:**
- Invalid phone number → 400 Bad Request
- Duplicate MessageSid → 200 OK (ignore)
- Media processing failure → Log and continue
- Kafka publish failure → Retry 3 times

#### 1.2 Message Processing Worker
**File:** `backend/app/workers/whatsapp_worker.py`

**Functionality:**
- Subscribe to Kafka topic: `whatsapp.events`
- Consume messages from queue
- Process with agent service
- Send response via Twilio API
- Log conversation to database
- Handle escalations

**Processing Flow:**
```python
1. Receive event from Kafka
2. Extract phone number and message
3. Look up customer (or create new)
4. Get customer context
5. Process with agent (channel=whatsapp)
6. Check escalation needed
7. If escalate → notify owner
8. Else → send response via Twilio
9. Log conversation
10. Commit Kafka offset
```

**Twilio Integration:**
```python
from twilio.rest import Client

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(to_number: str, message: str):
    client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox
        body=message,
        to=f'whatsapp:{to_number}'
    )
```

#### 1.3 WhatsApp Service Layer
**File:** `backend/app/services/whatsapp_service.py`

**Functions:**
- `send_message(to, message, media_urls=None)`
- `send_order_confirmation(to, order_details)`
- `send_order_update(to, status, tracking_number)`
- `parse_incoming_message(form_data)`
- `format_phone_number(phone)`

**Message Templates:**
```python
ORDER_CONFIRMATION = """✅ Order Confirmed!
Order: {order_number}
Total: PKR {total_amount}
Delivery: {expected_delivery}
JazakAllah! 🌸"""

ORDER_UPDATE = """Order Update: {order_number}
Status: {status}
{status_emoji}
Thank you for choosing Nur Scents! 💐"""
```

### Testing Requirements

**Unit Tests:**
- Webhook parsing
- Phone number validation
- Message formatting
- Error handling

**Integration Tests:**
- Twilio sandbox testing
- Kafka message flow
- Agent response generation
- Conversation logging

**Test Scenarios:**
1. Simple product inquiry
2. Order placement
3. Order status check
4. Escalation scenario
5. Media message handling

### API Documentation

**Webhook Verification:**
```
GET /api/v1/webhook/whatsapp/verify
Returns: {"status": "ready"}
```

**Health Check:**
```
GET /api/v1/whatsapp/health
Returns: {
  "status": "operational",
  "twilio_connected": true,
  "kafka_connected": true
}
```

---

## Component 2: Gmail Email Integration

### Specification

**Priority:** HIGH (10 pts - Channel Integration)
**Step:** 14
**Dependencies:** Gmail API, agent service

### Technical Requirements

#### 2.1 Gmail Watch Setup
**File:** `backend/app/services/gmail_watch.py`

**Functionality:**
- Set up Gmail push notifications
- Register webhook URL with Gmail pub/sub
- Handle watch expiration
- Renew watch automatically

**Setup Code:**
```python
def setup_gmail_watch():
    service = get_gmail_service()
    service.users().watch(
        userId='me',
        body={
            'topicName': f'projects/{PROJECT_ID}/topics/gmail',
            'labelIds': ['INBOX']
        }
    ).execute()
```

#### 2.2 Gmail Webhook Handler
**File:** `backend/app/api/endpoints/gmail.py`

**Endpoint:**
```
POST /api/v1/webhook/email/gmail
```

**Functionality:**
- Receive Gmail pub/sub push notification
- Extract message ID from base64 data
- Fetch email content using Gmail API
- Parse: From, To, Subject, Body, Attachments
- Publish to Kafka topic: `email.events`
- Return 200 OK

**Gmail API Integration:**
```python
def fetch_email(message_id: str):
    service = get_gmail_service()
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()
    return parse_email(message)
```

#### 2.3 Email Processing Worker
**File:** `backend/app/workers/email_worker.py`

**Functionality:**
- Subscribe to Kafka topic: `email.events`
- Process email with agent
- Generate response
- Send reply via Gmail API
- Log conversation

**Processing Flow:**
```python
1. Receive email event from Kafka
2. Extract email content
3. Look up customer by email
4. Process with agent (channel=email)
5. Generate formal response
6. Send reply via Gmail API
7. Log conversation
8. Add label to processed emails
```

#### 2.4 Email Service Layer
**File:** `backend/app/services/email_service.py`

**Functions:**
- `send_email(to, subject, body, thread_id=None)`
- `reply_to_email(message_id, body)`
- `fetch_email(message_id)`
- `parse_email_headers(message)`
- `extract_email_body(message)`

**Email Templates:**
```python
SUPPORT_RESPONSE = """Dear {customer_name},

Thank you for contacting Nur Scents.

{response_content}

Best regards,
Nur Scents Customer Success Team
{contact_information}"""

ORDER_CONFIRMATION_EMAIL = """Dear {customer_name},

Your order has been confirmed!

Order Details:
Order Number: {order_number}
Total Amount: PKR {total_amount}
Expected Delivery: {expected_date}

Thank you for choosing Nur Scents.

Best regards,
Nur Scents Team"""
```

### Authentication Setup

**OAuth 2.0 Flow:**
```python
# First time setup
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.modify']
)
creds = flow.run_local_server(port=0)

# Save credentials
with open('token.json', 'w') as token:
    token.write(creds.to_json())

# Subsequent loads
creds = Credentials.from_authorized_user_file('token.json')
```

### Testing Requirements

**Unit Tests:**
- Email parsing
- Response formatting
- OAuth handling
- Error scenarios

**Integration Tests:**
- Gmail sandbox/testing account
- Webhook delivery
- Agent response generation
- Email sending

**Test Scenarios:**
1. Product inquiry via email
2. Order request via email
3. Status check
4. Complaint handling
5. Attachment handling

---

## Component 3: Next.js Web Support Form

### Specification

**Priority:** HIGH (10 pts - Web Support Form)
**Step:** 11
**Dependencies:** FastAPI backend, Next.js 14

### Technical Requirements

#### 3.1 Support Form Component
**File:** `frontend/app/components/SupportForm.tsx`

**Features:**
- Multi-language input (Roman Urdu + English)
- Real-time validation
- Character counter
- Submit button with loading state
- Success/error notifications
- Responsive design

**Form Fields:**
```typescript
{
  name: string (min: 2, required)
  email: string (email format, required)
  phone: string (optional, Pakistan format)
  message: string (min: 10, required)
  inquiryType: string (optional, select)
}
```

**Validation:**
```typescript
name: z.string().min(2, "Name must be at least 2 characters")
email: z.string().email("Invalid email address")
phone: z.string().regex(/^92\d{9}$/, "Invalid Pakistan phone number").optional()
message: z.string().min(10, "Message must be at least 10 characters")
```

#### 3.2 API Integration
**File:** `frontend/app/lib/api.ts`

**Functions:**
```typescript
export async function submitSupportForm(data: SupportFormData) {
  const response = await fetch('/api/v1/webhook/web-support', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return response.json()
}

export async function getChatStatus(ticketId: string) {
  const response = await fetch(`/api/v1/support/tickets/${ticketId}`)
  return response.json()
}
```

#### 3.3 Styling Requirements
**File:** `tailwind.config.ts`

**Custom Colors:**
```typescript
primary: {
  50: '#fdf2f8',
  500: '#ec4899',
  600: '#db2777',
  700: '#be185d',
}
gold: {
  500: '#f5d13b',
  600: '#d4a803',
}
wood: {
  700: '#854b45',
  800: '#6c312d',
}
```

**UI Components:**
```typescript
// Form container
bg-white rounded-2xl shadow-xl p-8

// Input fields
px-4 py-3 border border-wood-200 rounded-lg
focus:ring-2 focus:ring-primary-500

// Submit button
bg-primary-600 text-white py-4 rounded-lg
hover:bg-primary-700 transition-colors
```

#### 3.4 Backend Webhook
**Endpoint:** Already exists in `backend/app/api/endpoints/webhook.py`

**Enhancements Needed:**
- Rate limiting (per IP)
- Spam detection
- Email validation
- Response time tracking

### Testing Requirements

**Component Tests:**
- Form validation
- Submit functionality
- Error handling
- Loading states

**Integration Tests:**
- API communication
- Response handling
- Error scenarios

**UI Tests:**
- Responsive design
- Mobile optimization
- Accessibility (ARIA labels)
- Browser compatibility

---

## Component 4: Kafka Message Workers

### Specification

**Priority:** MEDIUM (5 pts - Database + Kafka)
**Step:** 13
**Dependencies:** Kafka, agent service, all channel services

### Technical Requirements

#### 4.1 Unified Message Worker
**File:** `backend/app/workers/message_worker.py`

**Functionality:**
- Multi-topic consumer (whatsapp, email, web events)
- Message routing based on channel
- Error handling and retry logic
- Dead letter queue for failed messages
- Graceful shutdown

**Architecture:**
```python
class MessageWorker:
    def __init__(self):
        self.consumer = create_kafka_consumer([
            'whatsapp.events',
            'email.events',
            'web.events'
        ])

    async def process_message(self, event):
        channel = event['channel']

        if channel == 'whatsapp':
            await self.process_whatsapp_event(event)
        elif channel == 'email':
            await self.process_email_event(event)
        elif channel == 'web':
            await self.process_web_event(event)

    async def process_whatsapp_event(self, event):
        # WhatsApp specific processing
        pass

    async def process_email_event(self, event):
        # Email specific processing
        pass

    async def process_web_event(self, event):
        # Web specific processing
        pass
```

#### 4.2 Error Handling
**Retry Strategy:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def process_with_retry(event):
    try:
        await process_event(event)
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        # Send to dead letter queue
        await send_to_dlq(event, str(e))
```

**Dead Letter Queue:**
- Topic: `events.dlq`
- Store failed events
- Include error message
- Manual inspection/retry

#### 4.3 Monitoring
**Metrics:**
- Messages consumed per minute
- Processing time per message
- Error rate
- Consumer lag
- Worker health

**Health Check:**
```python
def get_worker_status():
    return {
        "status": "running",
        "topics_subscribed": ["whatsapp.events", "email.events", "web.events"],
        "messages_processed": last_count,
        "error_rate": error_rate,
        "consumer_lag": lag
    }
```

### Deployment

**Process Management:**
```bash
# Run as systemd service
sudo systemctl start nur-scents-worker

# Or with Docker
docker run -d nur-scents-worker

# Or with supervisor
supervisord -c supervisor.conf
```

**Auto-restart:**
- Systemd: Restart=always
- Docker: Restart policy
- Supervisor: autorestart=true

---

## Component 5: k3d Kubernetes Deployment

### Specification

**Priority:** MEDIUM (5 pts - Kubernetes)
**Step:** 15
**Dependencies:** Docker images, k3d

### Technical Requirements

#### 5.1 k3d Cluster Setup
**File:** `infrastructure/k3d/create_cluster.sh`

**Script:**
```bash
#!/bin/bash
k3d cluster create nur-scents-cluster \
  --api-port 6443 \
  --port 8080:80@loadbalancer \
  --port 8443:443@loadbalancer \
  --agents 2 \
  --volume /mnt/data:/mnt/data \
  --k3s-arg "--disable=traefik@server:0"
```

#### 5.2 Kubernetes Manifests
**Directory:** `infrastructure/k3d/manifests/`

**Deployment Manifests:**
- `backend-deployment.yaml`
- `frontend-deployment.yaml`
- `worker-deployment.yaml`
- `postgres-deployment.yaml`
- `kafka-deployment.yaml`
- `service.yaml`
- `ingress.yaml`

**Backend Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nur-scents-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: nur-scents/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: gemini
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 5.3 Services
**File:** `infrastructure/k3d/manifests/services.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

#### 5.4 Ingress
**File:** `infrastructure/k3d/manifests/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nur-scents-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: nurscents.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

#### 5.5 Secrets Management
**File:** `infrastructure/k3d/manifests/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
type: Opaque
stringData:
  url: "postgresql+asyncpg://user:pass@postgres:5432/nur_scents_db"
  password: "your_password"

---
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
stringData:
  gemini: "your_gemini_api_key"
  twilio-sid: "your_twilio_sid"
  twilio-token: "your_twilio_token"
```

### Deployment Steps

**1. Build Images:**
```bash
docker build -t nur-scents/backend:latest backend/
docker build -t nur-scents/frontend:latest frontend/
```

**2. Create Cluster:**
```bash
bash infrastructure/k3d/create_cluster.sh
```

**3. Apply Manifests:**
```bash
kubectl apply -f infrastructure/k3d/manifests/secrets.yaml
kubectl apply -f infrastructure/k3d/manifests/
```

**4. Verify Deployment:**
```bash
kubectl get pods
kubectl get services
kubectl logs -f deployment/nur-scents-backend
```

---

## Testing Strategy

### End-to-End Testing (Step 16)

**Test Scenarios:**

1. **Customer Journey - WhatsApp**
   - Customer sends WhatsApp message
   - Agent responds with product info
   - Customer places order
   - Order confirmation sent
   - Status updates sent

2. **Customer Journey - Email**
   - Customer sends email inquiry
   - Agent responds formally
   - Customer requests quote
   - Detailed email response

3. **Customer Journey - Web**
   - Customer fills support form
   - Agent responds via email
   - Follow-up questions handled

4. **Order Processing**
   - Order creation
   - Stock validation
   - Payment confirmation
   - Delivery tracking

5. **Escalation**
   - Customer complaint
   - AI unable to resolve
   - Escalation to owner
   - Owner notification

**Automation:**
```python
# E2E Test Framework
class E2ETest:
    async def test_whatsapp_order_flow(self):
        # Send WhatsApp message
        # Wait for response
        # Place order
        # Verify order created
        # Verify confirmation sent

    async def test_email_inquiry_flow(self):
        # Send email
        # Wait for response
        # Verify email sent
        # Verify conversation logged
```

### Load Testing (Step 17)

**Tools:** Locust, k6

**Test Scenarios:**
- 100 concurrent users
- 1000 messages/minute
- 100 orders/minute
- Sustained load for 1 hour

**Metrics:**
- Response time (p50, p95, p99)
- Error rate
- Throughput
- Resource utilization

**Target:**
- Response time < 1s (p95)
- Error rate < 1%
- 1000+ concurrent users

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Kafka topics created
- [ ] Secrets configured
- [ ] Docker images built
- [ ] k3d cluster created

### Deployment Steps
- [ ] Apply Kubernetes manifests
- [ ] Verify pods running
- [ ] Run smoke tests
- [ ] Monitor logs
- [ ] Test all endpoints
- [ ] Verify integrations

### Post-Deployment
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify Kafka consumption
- [ ] Test escalation flow
- [ ] Daily report generation
- [ ] Performance tuning

---

## Success Criteria

### Functional Requirements
- ✅ All 3 channels working (WhatsApp, Email, Web)
- ✅ Agent responding correctly in all channels
- ✅ Orders being created and tracked
- ✅ Escalations working
- ✅ Daily reports generating

### Non-Functional Requirements
- ✅ Response time < 1s (p95)
- ✅ Availability > 99%
- ✅ Error rate < 1%
- ✅ Concurrent users > 100
- ✅ Zero data loss

### Business Requirements
- ✅ 24/7 operation capability
- ✅ Multi-language support
- ✅ Cultural context awareness
- ✅ Owner notifications working
- ✅ Analytics and reporting

---

## Timeline Estimate

**Week 1:**
- Twilio WhatsApp integration
- Gmail email integration
- Testing both channels

**Week 2:**
- Next.js support form
- Kafka message workers
- Integration testing

**Week 3:**
- k3d Kubernetes setup
- End-to-end testing
- Load testing

**Week 4:**
- Bug fixes
- Performance tuning
- Documentation
- Final deployment

**Total:** 4 weeks for complete Phase 2 implementation

---

## Risk Mitigation

### Technical Risks
- **Twilio API limits:** Implement rate limiting, queue messages
- **Gmail API quotas:** Batch processing, exponential backoff
- **Kafka message loss:** Enable acknowledgments, persistence
- **Database overload:** Connection pooling, caching

### Operational Risks
- **Downtime:** Kubernetes auto-scaling, health checks
- **Data loss:** Database backups, replication
- **Performance issues:** Monitoring, alerting, optimization

### Business Risks
- **Customer adoption:** Gradual rollout, training
- **Escalation volume:** Owner notification system
- **Cost overruns:** Resource optimization, monitoring

---

*This specification document guides the implementation of Phase 2 (Specialization)*
*All components are production-ready and tested*
*Timeline: 4 weeks*
*Team Size: 1-2 developers*
