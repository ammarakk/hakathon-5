# Nur Scents Customer Success Agent - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.nurscents.pk
```

## Authentication
Currently, public endpoints. Future implementations will use JWT tokens for admin access.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information (debug mode only)"
}
```

---

## Health Check Endpoints

### GET /health
Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "nur-scents-agent",
  "version": "0.1.0"
}
```

### GET /ping
Simple ping for connectivity check.

**Response:**
```json
{
  "message": "pong"
}
```

### GET /
Root endpoint with service information.

**Response:**
```json
{
  "message": "Nur Scents Customer Success Agent",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## Product Endpoints

### GET /api/v1/products
Get all products with optional filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter by category (oudh, floral, musk, oriental, woody, bakhoor, bundle) |
| bestseller | boolean | No | Filter by bestseller status |
| min_price | float | No | Minimum price (PKR) |
| max_price | float | No | Maximum price (PKR) |

**Example Requests:**
```bash
# Get all products
GET /api/v1/products

# Get bestselling products
GET /api/v1/products?bestseller=true

# Get oudh products under 15000 PKR
GET /api/v1/products?category=oudh&max_price=15000
```

**Response:**
```json
{
  "success": true,
  "count": 12,
  "products": [
    {
      "id": "NS-001",
      "name": "Oudh Royale",
      "category": "Oudh",
      "description": "Premium quality Oudh with rich, woody notes...",
      "price": 12500,
      "stock": 25,
      "images": ["oudh_royale_front.jpg"],
      "tags": ["premium", "oudh", "long-lasting", "unisex"],
      "sizes": ["6ml", "12ml", "24ml"],
      "bestseller": true
    }
  ]
}
```

### GET /api/v1/products/{product_id}
Get details of a specific product.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | string | Yes | Product ID (e.g., NS-001) |

**Example Request:**
```bash
GET /api/v1/products/NS-001
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "NS-001",
    "name": "Oudh Royale",
    "category": "Oudh",
    "description": "Premium quality Oudh with rich, woody notes...",
    "price": 12500,
    "stock": 25,
    "images": ["oudh_royale_front.jpg", "oudh_royale_side.jpg"],
    "tags": ["premium", "oudh", "long-lasting", "unisex"],
    "sizes": ["6ml", "12ml", "24ml"],
    "bestseller": true
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Product with ID NS-999 not found"
}
```

### GET /api/v1/products/categories/list
Get all product categories.

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": "oudh",
      "name": "Oudh",
      "description": "Premium oudh fragrances"
    },
    {
      "id": "floral",
      "name": "Floral",
      "description": "Fresh floral scents"
    }
  ]
}
```

---

## Order Endpoints

### POST /api/v1/orders
Create a new order.

**Request Body:**
```json
{
  "customer_name": "Ahmed Khan",
  "phone_number": "+923001234567",
  "email": "ahmed@example.com",
  "address": "House 123, Street 4, Gulshan",
  "city": "Karachi",
  "products": [
    {
      "product_id": "NS-001",
      "quantity": 1,
      "size": "12ml"
    },
    {
      "product_id": "NS-003",
      "quantity": 2,
      "size": "6ml"
    }
  ],
  "payment_method": "Cash on Delivery",
  "total_amount": 21500
}
```

**Field Validation:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| customer_name | string | Yes | Min 2 chars |
| phone_number | string | Yes | Valid Pakistan phone format |
| email | string | No | Valid email if provided |
| address | string | Yes | Min 10 chars |
| city | string | Yes | Must be in delivery areas |
| products | array | Yes | Min 1 item |
| payment_method | string | Yes | Cash on Delivery, Bank Transfer, EasyPaisa, JazzCash |
| total_amount | float | Yes | Must match calculated total |

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "order_number": "NS-20260409223456",
    "customer_name": "Ahmed Khan",
    "phone_number": "+923001234567",
    "email": "ahmed@example.com",
    "address": "House 123, Street 4, Gulshan",
    "city": "Karachi",
    "products": [
      {
        "product_id": "NS-001",
        "product_name": "Oudh Royale",
        "quantity": 1,
        "size": "12ml",
        "price_per_unit": 12500,
        "subtotal": 12500
      },
      {
        "product_id": "NS-003",
        "product_name": "Musk Al Tahara",
        "quantity": 2,
        "size": "6ml",
        "price_per_unit": 4500,
        "subtotal": 9000
      }
    ],
    "payment_method": "Cash on Delivery",
    "total_amount": 21500,
    "delivery_charges": 0,
    "status": "pending",
    "created_at": "2026-04-09T22:34:56Z"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Validation error",
  "detail": {
    "city": "City not in delivery area",
    "products": "Product NS-001 is out of stock"
  }
}
```

### GET /api/v1/orders/{order_number}
Get order details and status.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order_number | string | Yes | Order number (e.g., NS-20260409223456) |

**Example Request:**
```bash
GET /api/v1/orders/NS-20260409223456
```

**Response:**
```json
{
  "success": true,
  "order": {
    "order_number": "NS-20260409223456",
    "status": "processing",
    "status_description": "Your order is being prepared",
    "customer": {
      "name": "Ahmed Khan",
      "phone": "+923001234567",
      "email": "ahmed@example.com"
    },
    "items": [
      {
        "product_id": "NS-001",
        "product_name": "Oudh Royale",
        "quantity": 1,
        "size": "12ml",
        "price": 12500
      }
    ],
    "payment": {
      "method": "Cash on Delivery",
      "status": "pending"
    },
    "delivery": {
      "address": "House 123, Street 4, Gulshan",
      "city": "Karachi",
      "charges": 0,
      "estimated_delivery": "2026-04-12"
    },
    "totals": {
      "subtotal": 21500,
      "delivery": 0,
      "total": 21500
    },
    "timeline": [
      {
        "status": "pending",
        "timestamp": "2026-04-09T22:34:56Z",
        "description": "Order placed"
      },
      {
        "status": "confirmed",
        "timestamp": "2026-04-09T22:35:30Z",
        "description": "Order confirmed"
      },
      {
        "status": "processing",
        "timestamp": "2026-04-10T09:00:00Z",
        "description": "Order is being prepared"
      }
    ],
    "created_at": "2026-04-09T22:34:56Z",
    "updated_at": "2026-04-10T09:00:00Z"
  }
}
```

---

## Webhook Endpoints

### POST /api/v1/webhook/whatsapp
Handle incoming WhatsApp messages from Twilio.

**Method:** POST
**Content-Type:** application/x-www-form-urlencoded

**Twilio Webhook Payload:**
```
MessageSid=SMxxxxx
From=whatsapp:+923001234567
Body=Oudh ki price kya hai?
Timestamp=2026-04-09T17:22:00Z
```

**Response:**
```json
{
  "success": true,
  "message": "WhatsApp webhook received"
}
```

**Processing Flow:**
1. Parse incoming message
2. Extract phone number and message body
3. Publish to `whatsapp.events` Kafka topic
4. Message worker processes event
5. AI agent generates response
6. Response sent via Twilio API

### GET /api/v1/webhook/whatsapp/verify
Verify Twilio webhook (for initial setup).

**Response:**
```json
{
  "success": true
}
```

### POST /api/v1/webhook/web-support
Handle web support form submissions.

**Request Body:**
```json
{
  "name": "Fatima Ali",
  "email": "fatima@example.com",
  "message": "I want to know about your floral attars collection",
  "phone": "+923009876543"
}
```

**Field Validation:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | string | Yes | Min 2 chars |
| email | string | Yes | Valid email |
| message | string | Yes | Min 10 chars |
| phone | string | No | Valid phone if provided |

**Response:**
```json
{
  "success": true,
  "message": "Support request received. We'll get back to you soon!",
  "ticket_id": "TICKET-20260409-001"
}
```

**Processing Flow:**
1. Validate form data
2. Publish to `web.events` Kafka topic
3. AI agent processes inquiry
4. Send email response to customer
5. Store conversation in database

### POST /api/v1/webhook/email/gmail
Handle Gmail push notifications.

**Method:** POST
**Content-Type:** application/json

**Gmail Pub/Sub Payload:**
```json
{
  "message": {
    "data": "<base64_encoded_message_id>",
    "messageId": "xxxxx",
    "publishTime": "2026-04-09T17:22:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gmail webhook received"
}
```

**Processing Flow:**
1. Receive Gmail push notification
2. Decode base64 message ID
3. Fetch email content via Gmail API
4. Parse email (sender, subject, body)
5. Publish to `email.events` Kafka topic
6. AI agent processes email
7. Send response via Gmail API

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Maintenance mode |

---

## Rate Limiting

Current limits (per IP):
- 60 requests per minute
- 10 orders per hour per phone number

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1704854400
```

---

## Example Usage

### Python Example
```python
import requests

# Get products
response = requests.get("http://localhost:8000/api/v1/products")
products = response.json()

# Create order
order_data = {
    "customer_name": "Ahmed Khan",
    "phone_number": "+923001234567",
    "email": "ahmed@example.com",
    "address": "House 123, Street 4, Gulshan",
    "city": "Karachi",
    "products": [
        {"product_id": "NS-001", "quantity": 1, "size": "12ml"}
    ],
    "payment_method": "Cash on Delivery",
    "total_amount": 12500
}

response = requests.post(
    "http://localhost:8000/api/v1/orders",
    json=order_data
)
order = response.json()
```

### JavaScript Example
```javascript
// Get products
const response = await fetch('http://localhost:8000/api/v1/products');
const data = await response.json();

// Create order
const orderData = {
    customer_name: "Ahmed Khan",
    phone_number: "+923001234567",
    email: "ahmed@example.com",
    address: "House 123, Street 4, Gulshan",
    city: "Karachi",
    products: [
        {product_id: "NS-001", quantity: 1, size: "12ml"}
    ],
    payment_method: "Cash on Delivery",
    total_amount: 12500
};

const response = await fetch('http://localhost:8000/api/v1/orders', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(orderData)
});
const order = await response.json();
```

---

## Future Endpoints (To Be Implemented)

### Customer Management
- `POST /api/v1/customers` - Register customer
- `GET /api/v1/customers/{id}` - Get customer profile
- `PUT /api/v1/customers/{id}` - Update customer profile
- `GET /api/v1/customers/{id}/orders` - Customer order history

### Admin Dashboard
- `GET /api/v1/admin/orders` - List all orders (paginated)
- `PUT /api/v1/admin/orders/{id}/status` - Update order status
- `GET /api/v1/admin/analytics` - Sales analytics
- `GET /api/v1/admin/reports` - Daily reports

### AI Agent
- `POST /api/v1/agent/chat` - Direct chat with agent (testing)
- `GET /api/v1/agent/status` - Agent operational status
- `POST /api/v1/agent/train` - Train/update agent (admin)

### Knowledge Base
- `GET /api/v1/kb/faq` - List FAQ items
- `POST /api/v1/kb/faq` - Add FAQ item (admin)
- `PUT /api/v1/kb/faq/{id}` - Update FAQ item (admin)
- `DELETE /api/v1/kb/faq/{id}` - Delete FAQ item (admin)

This API documentation will be updated as new endpoints are implemented.
