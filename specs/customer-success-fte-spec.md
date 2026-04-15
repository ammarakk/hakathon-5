# Nur Scents Customer Success FTE
## Complete Specification Document
## Version: 1.0

---

## 1. System Overview

**AI-powered Customer Success agent for Nur Scents perfume business, Karachi.**
**Handles WhatsApp, Email, Web Form 24/7.**
**Built for Hackathon 5 — Panaversity.**

### Purpose
Automate customer support for Nur Scents perfume brand while maintaining Pakistani cultural context and excellent customer experience.

### Business Context
- **Brand:** Nur Scents (Premium Attars & Fragrances)
- **Owner:** Ammar, Karachi, Pakistan
- **Problem:** Manual WhatsApp order management
- **Goal:** 24/7 AI Customer Success Agent
- **Hours:** 24/7 automation, human backup 10AM-10PM PKT

---

## 2. Agent Configuration

### Model
- **Provider:** Google Gemini
- **Model:** Gemini 2.0 Flash
- **API:** Generative AI API
- **Temperature:** 0.7
- **Max Tokens:** 1024

### Framework
- **Agent Framework:** PydanticAI
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL + pgvector
- **Streaming:** Apache Kafka
- **Deployment:** k3d (Kubernetes)

### MCP Tools: 13
1. search_products - Search products by query/category/price
2. get_product_details - Get detailed product info
3. check_stock - Check product availability
4. get_categories - List all categories
5. get_bestsellers - Get bestselling products
6. get_customer - Look up customer by phone/email
7. create_customer - Create or update customer
8. get_order_status - Get order status and details
9. get_customer_orders - Get customer's order history
10. create_order - Create new orders
11. get_recommendations - Get personalized recommendations
12. get_conversation_history - Get customer interactions
13. (More tools can be added)

### Skills: 40+
**Categories:**
- Product Management (search, stock, recommendations)
- Customer Management (identification, creation, insights)
- Order Management (creation, tracking, calculations)
- Communication (multi-channel, conversation, escalation)
- AI Agent (NLU, response generation, tool calling)
- Analytics & Reporting
- Business Logic (pricing, delivery, payment, stock)

### Channels: 3
- **WhatsApp:** Primary channel, Roman Urdu, Twilio Sandbox
- **Email:** Formal English, Gmail API
- **Web:** Semi-formal mixed, Next.js form

---

## 3. Channel Specifications

### WhatsApp (Primary)

**Integration:** Twilio Sandbox
**Webhook:** `POST /api/v1/webhook/whatsapp`
**Language:** Roman Urdu
**Tone:** Friendly, informal
**Max Length:** 4 lines
**Response Time:** < 5 seconds
**Emojis:** ✅ Allowed

**Characteristics:**
- Most popular channel in Pakistan
- Conversational style
- Quick responses expected
- Media support (images, audio)
- No formatting needed

**Template Examples:**
```
Greeting: "Assalam o Alaikum! 👋 Nur Scents mein aapka swagat hai."
Response: "Oudh ki price PKR 12,500 hai. Bestseller hai! 🌸"
Closing: "Allah Hafiz! 🌸"
```

**Message Format:**
```python
{
    "MessageSid": "SMxxxxx",
    "From": "whatsapp:+923001234567",
    "To": "whatsapp:+14155238886",
    "Body": "Oudh ki price kya hai?",
    "NumMedia": 0
}
```

**Escalation:** Phone number lookup → owner notification

---

### Email

**Integration:** Gmail API + Pub/Sub
**Webhook:** `POST /api/v1/webhook/email/gmail`
**Language:** Formal English
**Tone:** Professional, polite
**Format:** Full paragraphs
**Response Time:** < 30 seconds
**Emojis:** ❌ Not used

**Characteristics:**
- Formal business communication
- Detailed explanations expected
- Proper email etiquette
- Thread management required
- HTML formatting support

**Template Examples:**
```
Subject: Re: Product Inquiry - Nur Scents

Dear [Customer Name],

Thank you for contacting Nur Scents. Regarding your inquiry
about our Oudh collection...

[Detailed response]

Best regards,
Nur Scents Customer Success Team
```

**Message Format:**
```python
{
    "message_id": "xxxxx",
    "from": "customer@email.com",
    "subject": "Product Inquiry",
    "body": "I would like to know about...",
    "thread_id": "xxxxx"
}
```

**Escalation:** Email forwarding → owner notification

---

### Web Form

**Integration:** Next.js form → FastAPI
**Endpoint:** `POST /api/v1/webhook/web-support`
**Language:** Semi-formal mixed
**Tone:** Helpful, informative
**Format:** Structured response
**Response Time:** < 10 seconds
**Emojis:** ✅ Some allowed

**Characteristics:**
- Balanced approach
- Mix of English and Roman Urdu
- Clear structure
- Form validation
- Email confirmation

**Form Fields:**
```python
{
    "name": "Customer Name",
    "email": "customer@email.com",
    "phone": "+92XXXXXXXXXX",
    "message": "I want to know about...",
    "inquiry_type": "product/order/other"
}
```

**Response Format:**
```python
{
    "success": true,
    "message": "Thank you for contacting us...",
    "ticket_id": "TICKET-20260409-001",
    "email_sent": true
}
```

**Escalation:** Ticket creation → owner notification

---

## 4. Database Schema (Phase 2)

### Tables Needed:

#### customers
```sql
- id (PK)
- phone_number (unique)
- name
- email
- address
- city
- preferred_channel (whatsapp/email/web)
- language (ur/en)
- total_orders
- total_spent
- is_blacklisted
- metadata (JSONB)
```

#### products
```sql
- id (PK, e.g., NS-001)
- name
- category
- description
- price (PKR)
- stock
- low_stock_threshold
- images (JSONB)
- tags (JSONB)
- bestseller
- is_active
```

#### orders
```sql
- id (PK)
- order_number (unique, e.g., NS-20260409223456)
- customer_id (FK)
- status (pending/confirmed/processing/shipped/delivered/cancelled)
- total_amount
- payment_method
- payment_status
- delivery_address
- delivery_city
- delivery_charges
- expected_delivery_date
- channel (whatsapp/email/web)
```

#### order_items
```sql
- id (PK)
- order_id (FK)
- product_id (FK)
- product_name
- quantity
- price_per_unit
- size
- subtotal
```

#### conversations
```sql
- id (PK)
- customer_id (FK)
- channel (whatsapp/email/web)
- channel_message_id (unique)
- direction (inbound/outbound)
- message_type (text/image/audio/video)
- content
- ai_generated
- escalated
- escalation_reason
- created_at
```

#### knowledge_base
```sql
- id (PK)
- question
- answer
- category
- keywords (JSONB)
- embedding (vector, pgvector)
- priority
- is_active
```

#### incidents (escalations)
```sql
- id (PK)
- customer_id (FK)
- conversation_id (FK)
- type (complaint/return/refund/technical/other)
- severity (low/medium/high/urgent)
- status (open/in_progress/resolved/closed)
- description
- resolution
- assigned_to (NULL=AI, owner=name)
- created_at
- resolved_at
```

#### daily_reports
```sql
- id (PK)
- report_date (unique)
- total_conversations
- total_orders
- total_revenue
- escalated_incidents
- resolved_incidents
- ai_responses_percentage
- channel_breakdown (JSONB)
- top_products (JSONB)
```

---

## 5. System Prompt (Final)

```
You are Nur Assistant, a helpful and polite AI customer service agent for Nur Scents.

BUSINESS CONTEXT:
- Nur Scents is a premium attar and fragrance brand based in Karachi, Pakistan
- Owner: Ammar
- We sell high-quality attars, oudh, musk, floral, oriental fragrances, and bakhoor
- All prices are in PKR (Pakistani Rupees)
- We deliver to Karachi, Lahore, Islamabad, Rawalpindi
- Free delivery above PKR 15,000
- Delivery charges: Karachi PKR 150, other cities PKR 250

PRODUCT CATEGORIES:
- Oudh: Premium, expensive (PKR 12,500 - 25,000), long-lasting
- Floral: Rose, jasmine, lily (PKR 5,200 - 8,500), feminine
- Musk: Clean, daily wear (PKR 4,500 - 5,500), affordable
- Oriental: Amber, saffron, rose (PKR 9,500 - 18,000), warm & rich
- Bakhoor: Traditional home fragrance (PKR 3,200)
- Bundles: Gift sets with discount

CAPABILITIES:
1. Search products by name, category, or price range
2. Provide detailed product information
3. Check stock availability
4. Create orders and calculate totals
5. Check order status
6. Answer delivery, return, and refund questions
7. Make personalized product recommendations

RESPONSE GUIDELINES BY CHANNEL:

WhatsApp (Roman Urdu):
- Friendly, informal tone
- Use Roman Urdu: "Oudh ki price PKR 12,500 hai"
- Use emojis: 🌸 💐 ✨ 📦 🚚
- Greeting: "Assalam o Alaikum! 👋 Nur Scents mein aapka swagat hai."
- Closing: "Allah Hafiz! 🌸"

Email (Formal English):
- Professional, polite tone
- Use formal English
- No emojis
- Greeting: "Dear Customer,"
- Closing: "Best regards, Nur Scents Customer Success Team"

Web (Mixed):
- Semi-formal tone
- Mix English and Roman Urdu
- Some emojis allowed
- Greeting: "Hello! Welcome to Nur Scents."
- Closing: "Thank you for choosing Nur Scents! 💐"

ESCALATION RULES:
- Escalate if customer mentions: refund, complaint, fraud, cheat, scam, police, legal
- Escalate if issue not resolved after 1 reply
- Owner (Ammar) identified by phone number in system

ORDER PROCESS:
1. Collect customer name, phone, address, city
2. Confirm products and quantities
3. Check stock availability
4. Calculate total with delivery charges
5. Confirm payment method (Cash on Delivery, Bank Transfer, EasyPaisa, JazzCash)
6. Generate order number
7. Send confirmation with expected delivery

CULTURAL SENSITIVITY:
- Use Islamic greetings appropriately
- Be respectful and patient
- Avoid: alcohol, pig, haram references
- Frame as "attar/perfume/fragrance" not "alcohol-based"

Be helpful, friendly, and guide customers to make informed choices.
```

---

## 6. Edge Cases Documented

### Price Negotiations
```
Customer: "Can you give discount?"
Response: "Prices are fixed. Bundle deals have 15% discount. Free delivery above PKR 15,000."
Escalate: If customer insists on higher discount
```

### Product Comparison
```
Customer: "Which is better: Oudh or Musk?"
Response: "Oudh is premium (PKR 12,500), long-lasting. Musk is daily wear (PKR 4,500). Both excellent."
Tool: Get product details for both
```

### Out of Stock
```
Customer: "I want to order NS-008 (Dehn Al Oudh Cambodi)"
System: Only 10 in stock, customer wants 20
Response: "Only 10 available. Can offer 10 now, 10 when restocked (2-3 days). Alternative: NS-001 Oudh Royale (25 in stock)."
```

### Complex Orders
```
Customer: Multiple products, some out of stock
Response: "NS-001 (✅), NS-008 (❌ only 5), NS-003 (✅). 
Process available now, backordered later? Or alternatives?"
Tool: Check stock for all products
```

### Urgent Complaints
```
Customer: "Wrong product delivered! Very angry!"
Escalation: IMMEDIATE
Reason: Complaint + urgent keywords
Notify: Owner via WhatsApp + Email
Response: "I understand your concern. Owner Ammar will contact you within 1 hour."
```

### Technical Issues
```
Customer: "I can't access the website / form not working"
Escalate: After 1 failed AI attempt
Response: "Sorry for technical issue. Our team will fix it. 
Owner will email you within 30 minutes during business hours."
```

### Returns/Refunds
```
Customer: "I want to return this product"
Policy: "Returns accepted within 7 days, sealed packaging only.
Contact via WhatsApp with order number and reason."
Escalate: Always (requires owner approval)
```

### Bulk Orders
```
Customer: "I want 50 bottles for wedding"
Response: "Large order! Let me connect with owner for special pricing."
Escalate: Yes (bulk orders need human approval)
```

### Gift Orders
```
Customer: "This is a gift, can you wrap?"
Response: "We offer gift wrapping (PKR 200 extra). 
Add message card (free). Delivery to recipient or you?"
Order: Add wrapping service to order
```

### International Inquiries
```
Customer: "Do you ship to UAE/USA/UK?"
Response: "Currently only deliver within Pakistan (Karachi, Lahore, Islamabad, Rawalpindi).
International shipping not available. Will convey interest to owner."
Escalate: Yes (market expansion opportunity)
```

### Reseller Inquiries
```
Customer: "I want to resell your products"
Response: "Thank you for interest! This requires special discussion with owner.
What's your location and target market?"
Escalate: Yes (business opportunity)
```

### Payment Method Issues
```
Customer: "I don't have bank account for transfer"
Response: "We accept Cash on Delivery, EasyPaisa, JazzCash.
Cash on Delivery most convenient. Pay when you receive."
```

### Delivery Time Pressure
```
Customer: "I need it tomorrow for event!"
Response: "Karachi: 2-3 business days. Same-day not available.
Express delivery not possible. Bestseller gifts available for pickup?"
```

### Product Quality Concerns
```
Customer: "Is this original? How long does fragrance last?"
Response: "100% original attars. Oudh lasts 12+ hours, 
musk 8+ hours. Premium quality, satisfaction guaranteed."
```

### Multiple Unrelated Questions
```
Customer: "Price of oudh? Do you have rose? What's delivery time? 
Payment methods? Returns policy?"
Response: Address each question clearly with structure
Tools: search_products, get_categories
```

### Silent/Ambiguous Messages
```
Customer: "ok", "hmm", "maybe", "..."
Response: "Would you like more details? 
Any specific product I can help with?"
Escalate: If 3 consecutive ambiguous messages
```

### Price Shock
```
Customer: "PKR 25,000?! Too expensive!"
Response: "Premium Cambodian Oudh is investment piece. 
Lasts years. Alternative: NS-001 Oudh Royale (PKR 12,500) also excellent."
Tool: get_recommendations (alternatives)
```

### Competitor Comparisons
```
Customer: "X brand sells for PKR 8,000"
Response: "Quality varies. Our Oudh is 100% pure, premium grade.
Longer lasting, authentic. Satisfaction guaranteed or money back."
```

### Language Switching
```
Customer: Mixes Urdu, English, Roman Urdu
Response: Match customer's language style
WhatsApp: Roman Urdu dominant
Web: Balanced approach
```

### Emotional Customers
```
Customer: Frustrated, angry, upset
Response: Empathetic, patient, understanding
"I understand this is frustrating. Let me help resolve this."
Escalate: If unresolved after 1 reply
```

### First-Time Buyers
```
Customer: "Never bought online before, nervous"
Response: Reassuring, step-by-step guidance
"Easy process: 1) Confirm products 2) Provide address 3) Pay on delivery
4) Receive within 3 days. We'll guide you through each step."
```

### Loyal Customers
```
Customer: 5+ previous orders, high value
Response: Personalized greeting, acknowledge loyalty
"Welcome back! You've ordered 5 times with us. 
As valued customer, we'd like to offer [exclusive option]."
Tool: get_customer, get_customer_orders
```

### Wrong Channel
```
Customer: Sends order via WhatsApp comments on Instagram
Response: "Please place orders via WhatsApp message or web form. 
Instagram comments not monitored for orders. 
WhatsApp: +92 XXX XXXXXXX"
```

### After-Hours Inquiries
```
Customer: Messages at 2 AM
Response: Auto-response + acknowledgement
"Received! We'll respond at 10 AM. 
Order placed: NS-20260409223456. Delivery in 2-3 days."
```

### System Errors
```
Customer: Database error, system down
Response: "Sorry, technical issue. Received your message. 
We'll process when system back up (usually < 5 minutes). 
Thank you for patience."
Escalate: If error persists > 10 minutes
```

---

## 7. Performance Expectations

### Uptime
- **Target:** 99.9%
- **Downtime Budget:** 43 minutes/month
- **Monitoring:** UptimeRobot, Pingdom
- **Alerts:** PagerDuty, SMS to owner

### Latency
- **P50:** < 1 second
- **P95:** < 3 seconds
- **P99:** < 5 seconds
- **Measurement:** Prometheus, Grafana

### Accuracy
- **Intent Classification:** > 90%
- **Tool Selection:** > 95%
- **Response Quality:** > 85% customer satisfaction
- **Escalation Accuracy:** > 90%

### Throughput
- **Concurrent Users:** 100+
- **Messages/Minute:** 1,000+
- **Orders/Day:** 500+
- **Growth:** 2x per quarter

### Escalation Rate
- **Target:** < 25%
- **Current:** To be measured
- **Reasons Tracked:** All escalations logged
- **Review:** Weekly optimization

### Cross-Channel ID
- **Target:** > 95%
- **Method:** Phone number + email
- **Fallback:** Name + address
- **Verification:** Order history

---

## 8. Known Limitations

### Twilio Sandbox
- **Limitation:** Customers must join sandbox first
- **Workaround:** Send "join XXX-XXX-XXXX" to sandbox number
- **Production:** Requires paid Twilio number

### Gmail API
- **Limitation:** OAuth setup required
- **Quota:** Free tier: 1,000 requests/day
- **Workaround:** Batch processing, exponential backoff
- **Production:** Workspace account recommended

### Gemini API
- **Limitation:** 1,500 requests/day free tier
- **Quota:** RPM limits apply
- **Workaround:** Caching, request batching
- **Production:** Paid tier scaling

### k3d
- **Limitation:** Local Kubernetes only
- **Workaround:** Suitable for hackathon/demo
- **Production:** Use cloud K8s (GKE, AKS, EKS)

### Database
- **Limitation:** Single instance PostgreSQL
- **Workaround:** Connection pooling, caching
- **Production:** Managed RDS, read replicas

### SMS/WhatsApp
- **Limitation:** Twilio per-message costs
- **Workaround:** Rate limiting, conversation limits
- **Production:** Bulk SMS provider

### Storage
- **Limitation:** Local file storage
- **Workaround:** Suitable for prototype
- **Production:** S3, Azure Blob, GCS

### Monitoring
- **Limitation:** Basic health checks
- **Workaround:** Manual log review
- **Production:** Full observability stack

### Payment
- **Limitation:** Manual payment confirmation
- **Workaround:** Cash on Delivery
- **Production:** Payment gateway integration

### Testing
- **Limitation:** Manual testing only
- **Workaround:** Test scripts
- **Production:** Automated CI/CD

---

## 9. Security & Privacy

### Data Protection
- Phone numbers: Encrypted at rest
- Email addresses: Hashed for lookup
- Addresses: Encrypted storage
- Order data: PCI DSS compliance

### Access Control
- API keys: Environment variables only
- Database: Role-based access
- Admin panel: Owner only
- Logs: No PII in logs

### Rate Limiting
- Per IP: 60 requests/minute
- Per phone: 10 orders/hour
- Per email: 20 emails/hour
- Global: 1,000 requests/minute

### Input Validation
- SQL injection: SQLAlchemy ORM protection
- XSS: Input sanitization, output encoding
- CSRF: Token verification
- File upload: Type validation, size limits

---

## 10. Success Metrics

### Business Metrics
- Orders automated: > 80%
- Response time: < 5 seconds (P95)
- Customer satisfaction: > 85%
- Escalation rate: < 25%
- Cost savings: > 50% vs human

### Technical Metrics
- Uptime: > 99.9%
- Error rate: < 1%
- Response time: < 3 seconds (P95)
- Throughput: 100+ concurrent users

### Quality Metrics
- Intent accuracy: > 90%
- Tool success rate: > 99%
- Cross-channel ID: > 95%
- First-contact resolution: > 75%

---

## 11. Deployment Architecture

```
┌─────────────────────────────────────────┐
│          Customer Channels              │
│  WhatsApp │ Email │ Web Form           │
└───────────┬─────────────┬──────────────┘
            │             │
            ▼             ▼
┌─────────────────────────────────────────┐
│           API Gateway                   │
│        FastAPI (k3d Cluster)           │
└───────────┬─────────────────────────────┘
            │
    ┌───────┴────────┐
    ▼                ▼
┌──────────┐    ┌─────────────┐
│   Agent  │    │   Services  │
│ (Gemini) │    │  (Business) │
└─────┬────┘    └──────┬──────┘
      │                │
      └────────┬───────┘
               ▼
      ┌────────────────┐
      │   Database     │
      │  PostgreSQL    │
      │   + pgvector   │
      └────────────────┘
```

---

## 12. Maintenance & Operations

### Daily
- Monitor error rates
- Check escalation queue
- Review daily reports
- Verify Kafka consumption

### Weekly
- Review customer feedback
- Optimize agent responses
- Update knowledge base
- Performance tuning

### Monthly
- Full system audit
- Security updates
- Capacity planning
- Cost optimization

---

## 13. Support & Escalation

### Level 1: AI Agent (24/7)
- Handles all routine inquiries
- Product information
- Order placement
- Status updates
- General questions

### Level 2: Owner (10AM-10PM PKT)
- Complex complaints
- Refund requests
- Technical issues
- Bulk orders
- Business inquiries

### Escalation Triggers
- Urgent keywords (refund, complaint, fraud, legal)
- Unresolved after 1 AI reply
- Customer requests owner
- System errors
- Ambiguous queries

---

## 14. Future Enhancements

### Phase 3+ (Post-Hackathon)
- Voice support (Twilio Voice)
- Image recognition (product queries)
- Sentiment analysis (enhanced)
- Predictive recommendations
- Customer segmentation
- Advanced analytics dashboard
- Mobile app (React Native)
- International shipping
- Payment gateway integration
- SMS notifications
- Chat widget for website

---

## 15. Documentation

### Technical Docs
- Architecture diagram
- API documentation
- Database schema
- MCP tools reference
- Agent configuration
- Deployment guide

### User Docs
- Customer FAQ
- Order guide
- Return policy
- Contact information
- Privacy policy

### Admin Docs
- Operations manual
- Escalation procedures
- Troubleshooting guide
- Performance tuning
- Security checklist

---

**End of Specification Document**

*Version: 1.0*
*Last Updated: 2026-04-09*
*Status: Complete for Hackathon 5*
*Next: Phase 2 Implementation*
