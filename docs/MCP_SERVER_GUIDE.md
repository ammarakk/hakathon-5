# MCP Server Documentation

## Overview

The **MCP (Model Context Protocol) Server** for Nur Scents exposes business capabilities as callable tools that AI agents can use to interact with the system.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent (Gemini)                    │
│  - Processes customer messages                        │
│  - Decides which tools to use                         │
│  - Generates responses                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server Layer                      │
│  - Exposes 13 business tools                          │
│  - Handles tool execution                             │
│  - Returns structured results                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│  ProductService │ CustomerService │ OrderService       │
│  ConversationService │ AgentService                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Database Layer                         │
│  PostgreSQL + pgvector                                 │
└─────────────────────────────────────────────────────────┘
```

## Available Tools

### 1. search_products
Search for products by name, category, or price range.

**Parameters:**
- `query` (required): Search query
- `category` (optional): Filter by category
- `min_price` (optional): Minimum price in PKR
- `max_price` (optional): Maximum price in PKR
- `limit` (optional): Maximum results (default: 10)

**Returns:**
```json
{
  "success": true,
  "count": 3,
  "products": [...]
}
```

### 2. get_product_details
Get detailed information about a specific product.

**Parameters:**
- `product_id` (required): Product ID (e.g., NS-001)

**Returns:**
```json
{
  "success": true,
  "product": {
    "id": "NS-001",
    "name": "Oudh Royale",
    "price": 12500,
    "stock": 25,
    ...
  }
}
```

### 3. check_stock
Check if products are in stock.

**Parameters:**
- `product_id` (required): Product ID to check
- `quantity` (optional): Required quantity (default: 1)

**Returns:**
```json
{
  "success": true,
  "stock": {
    "product_id": "NS-001",
    "available_stock": 25,
    "can_fulfill": true,
    "in_stock": true
  }
}
```

### 4. get_categories
Get all product categories.

**Returns:**
```json
{
  "success": true,
  "categories": [...]
}
```

### 5. get_bestsellers
Get bestselling products for recommendations.

**Parameters:**
- `limit` (optional): Number of products (default: 5)

**Returns:**
```json
{
  "success": true,
  "count": 5,
  "products": [...]
}
```

### 6. get_customer
Get customer information.

**Parameters:**
- `phone` (optional): Customer phone number
- `email` (optional): Customer email address

**Returns:**
```json
{
  "success": true,
  "customer": {
    "id": 1,
    "name": "Ahmed Khan",
    "phone_number": "+923001234567",
    ...
  }
}
```

### 7. create_customer
Create or update customer.

**Parameters:**
- `phone` (required): Phone number
- `name` (required): Customer name
- `email` (optional): Email address
- `address` (optional): Address
- `city` (optional): City
- `preferred_channel` (optional): whatsapp, email, web

**Returns:**
```json
{
  "success": true,
  "customer": {...},
  "message": "Customer created/updated successfully"
}
```

### 8. get_order_status
Get order status and details.

**Parameters:**
- `order_number` (required): Order number

**Returns:**
```json
{
  "success": true,
  "order": {
    "order_number": "NS-20260409223456",
    "status": "processing",
    ...
  }
}
```

### 9. get_customer_orders
Get all orders for a customer.

**Parameters:**
- `phone` (required): Customer phone number
- `limit` (optional): Maximum orders (default: 10)

**Returns:**
```json
{
  "success": true,
  "count": 3,
  "orders": [...]
}
```

### 10. create_order
Create a new order.

**Parameters:**
- `customer_phone` (required): Phone number
- `customer_name` (required): Customer name
- `products` (required): Array of product items
- `address` (required): Delivery address
- `city` (required): Delivery city
- `payment_method` (required): Payment method
- `channel` (optional): whatsapp, email, web

**Returns:**
```json
{
  "success": true,
  "order": {
    "order_number": "NS-20260409223456",
    "total_amount": 12500,
    ...
  },
  "message": "Order created successfully"
}
```

### 11. get_recommendations
Get personalized product recommendations.

**Parameters:**
- `preferences` (optional): Customer preferences
- `limit` (optional): Number of recommendations (default: 5)

**Returns:**
```json
{
  "success": true,
  "count": 5,
  "recommendations": [...]
}
```

### 12. get_conversation_history
Get conversation history for a customer.

**Parameters:**
- `phone` (required): Customer phone number
- `limit` (optional): Number of conversations (default: 10)

**Returns:**
```json
{
  "success": true,
  "count": 5,
  "conversations": [...]
}
```

## API Endpoints

### List All Tools
```
GET /api/v1/mcp/tools
```

### Get Tool Information
```
GET /api/v1/mcp/tools/{tool_name}
```

### Call Tool Directly
```
POST /api/v1/mcp/tools/call

{
  "tool_name": "search_products",
  "parameters": {
    "query": "oudh",
    "limit": 5
  }
}
```

### Chat with Enhanced Agent
```
POST /api/v1/mcp/agent/chat

{
  "message": "What oudh products do you have?",
  "channel": "whatsapp",
  "customer_context": {...}
}
```

### Get MCP Server Status
```
GET /api/v1/mcp/status
```

## Usage Examples

### Example 1: Search Products
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_products",
    "parameters": {
      "query": "oudh",
      "limit": 3
    }
  }'
```

### Example 2: Check Stock
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "check_stock",
    "parameters": {
      "product_id": "NS-001",
      "quantity": 5
    }
  }'
```

### Example 3: Create Order
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_order",
    "parameters": {
      "customer_phone": "+923001234567",
      "customer_name": "Ahmed Khan",
      "products": [
        {
          "product_id": "NS-001",
          "quantity": 1,
          "size": "12ml"
        }
      ],
      "address": "House 123, Street 4, Gulshan",
      "city": "Karachi",
      "payment_method": "Cash on Delivery",
      "channel": "whatsapp"
    }
  }'
```

### Example 4: Chat with Enhanced Agent
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to order oudh",
    "channel": "whatsapp"
  }'
```

## Testing

Run the MCP server test suite:

```bash
cd backend
python scripts/test_mcp.py
```

This will test:
- All 13 MCP tools
- Enhanced agent with tool integration
- Direct tool calling
- Error handling

## Benefits

### 1. Modular Design
Each tool is independent and can be used separately or combined.

### 2. Type Safety
All tools have defined parameter schemas with validation.

### 3. Consistent Interface
All tools follow the same request/response pattern.

### 4. Easy Integration
AI agents can easily call tools through the MCP protocol.

### 5. Extensible
New tools can be added without modifying existing code.

## Integration with AI Agents

The MCP server integrates seamlessly with AI agents:

1. **Agent receives message** from customer
2. **Agent analyzes message** to determine intent
3. **Agent calls appropriate MCP tools**
4. **MCP server executes tools** and returns results
5. **Agent generates response** using tool results
6. **Response sent to customer**

This enables the AI agent to:
- Search and recommend products
- Check stock availability
- Create and manage orders
- Look up customer information
- Track conversations

## Future Enhancements

Potential additions to the MCP server:

- **Analytics Tools**: Sales data, popular products
- **Report Generation**: Daily/weekly reports
- **Inventory Management**: Stock alerts, low stock warnings
- **Customer Insights**: Purchase history, preferences
- **Promotions**: Discount codes, special offers

## Troubleshooting

### Tool Not Found
If a tool returns "not found", check:
- Tool name is spelled correctly
- Tool is registered in MCP server
- Server is running

### Parameter Validation Errors
If parameters are invalid:
- Check parameter types match schema
- Required parameters are provided
- Values are within allowed ranges

### Database Errors
If database operations fail:
- Check database connection
- Verify data exists
- Check for constraint violations

## Support

For issues or questions about the MCP server:
1. Check the logs: `backend/logs/app.log`
2. Run tests: `python scripts/test_mcp.py`
3. Review tool definitions in `backend/app/mcp/server.py`

The MCP server is a powerful interface that enables AI agents to interact with the Nur Scents system in a structured, reliable way.
