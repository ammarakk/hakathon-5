"""
MCP (Model Context Protocol) Server for Nur Scents
Exposes system capabilities as tools for AI agents
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import product_service
from app.services.customer_service import customer_service
from app.services.order_service import order_service
from app.services.conversation_service import conversation_service
from app.models.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server for Nur Scents Customer Success Agent

    Exposes business capabilities as callable tools for AI agents
    following the Model Context Protocol specification.
    """

    def __init__(self):
        """Initialize MCP server with all tools"""
        self.tools = self._register_tools()
        logger.info(f"✅ MCP Server initialized with {len(self.tools)} tools")

    def _register_tools(self) -> Dict[str, Dict]:
        """
        Register all available tools

        Returns:
            Dictionary of tool definitions
        """
        return {
            "search_products": {
                "name": "search_products",
                "description": "Search for products by name, category, or price range. Returns list of matching products with details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (product name, category, or description)"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category (oudh, floral, musk, oriental, woody, bakhoor, bundle)",
                            "enum": ["oudh", "floral", "musk", "oriental", "woody", "bakhoor", "bundle"]
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price in PKR"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price in PKR"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            "get_product_details": {
                "name": "get_product_details",
                "description": "Get detailed information about a specific product by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "Product ID (e.g., NS-001, NS-002)"
                        }
                    },
                    "required": ["product_id"]
                }
            },
            "check_stock": {
                "name": "check_stock",
                "description": "Check if products are in stock and available. Returns availability status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "Product ID to check"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Required quantity",
                            "default": 1
                        }
                    },
                    "required": ["product_id"]
                }
            },
            "get_categories": {
                "name": "get_categories",
                "description": "Get list of all product categories.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_bestsellers": {
                "name": "get_bestsellers",
                "description": "Get bestselling products. Great for recommendations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of products to return",
                            "default": 5
                        }
                    },
                    "required": []
                }
            },
            "get_customer": {
                "name": "get_customer",
                "description": "Get customer information by phone number or email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number (e.g., +923001234567)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Customer email address"
                        }
                    }
                },
                "required": []
                # At least one of phone or email should be provided
            },
            "create_customer": {
                "name": "create_customer",
                "description": "Create a new customer or update existing customer information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "name": {
                            "type": "string",
                            "description": "Customer name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Customer email"
                        },
                        "address": {
                            "type": "string",
                            "description": "Customer address"
                        },
                        "city": {
                            "type": "string",
                            "description": "Customer city"
                        },
                        "preferred_channel": {
                            "type": "string",
                            "description": "Preferred communication channel",
                            "enum": ["whatsapp", "email", "web"],
                            "default": "whatsapp"
                        }
                    },
                    "required": ["phone", "name"]
                }
            },
            "get_order_status": {
                "name": "get_order_status",
                "description": "Get order status and details by order number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_number": {
                            "type": "string",
                            "description": "Order number (e.g., NS-20260409223456)"
                        }
                    },
                    "required": ["order_number"]
                }
            },
            "get_customer_orders": {
                "name": "get_customer_orders",
                "description": "Get all orders for a customer by phone number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of orders",
                            "default": 10
                        }
                    },
                    "required": ["phone"]
                }
            },
            "create_order": {
                "name": "create_order",
                "description": "Create a new order. Returns order number and details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name"
                        },
                        "products": {
                            "type": "array",
                            "description": "List of products to order",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {
                                        "type": "string",
                                        "description": "Product ID"
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Quantity"
                                    },
                                    "size": {
                                        "type": "string",
                                        "description": "Product size (optional)"
                                    }
                                },
                                "required": ["product_id", "quantity"]
                            }
                        },
                        "address": {
                            "type": "string",
                            "description": "Delivery address"
                        },
                        "city": {
                            "type": "string",
                            "description": "Delivery city"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method",
                            "enum": ["Cash on Delivery", "Bank Transfer", "EasyPaisa", "JazzCash"]
                        },
                        "channel": {
                            "type": "string",
                            "description": "Order channel",
                            "enum": ["whatsapp", "email", "web"],
                            "default": "web"
                        }
                    },
                    "required": ["customer_phone", "customer_name", "products", "address", "city", "payment_method"]
                }
            },
            "get_recommendations": {
                "name": "get_recommendations",
                "description": "Get personalized product recommendations based on customer preferences.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "preferences": {
                            "type": "string",
                            "description": "Customer preferences (e.g., 'floral scents under 10000')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of recommendations",
                            "default": 5
                        }
                    },
                    "required": []
                }
            },
            "get_conversation_history": {
                "name": "get_conversation_history",
                "description": "Get recent conversation history for a customer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of conversations",
                            "default": 10
                        }
                    },
                    "required": ["phone"]
                }
            }
        }

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call

        Args:
            tool_name: Name of the tool to call
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        async with AsyncSessionLocal() as db:
            try:
                if tool_name == "search_products":
                    return await self._search_products(db, parameters)
                elif tool_name == "get_product_details":
                    return await self._get_product_details(db, parameters)
                elif tool_name == "check_stock":
                    return await self._check_stock(db, parameters)
                elif tool_name == "get_categories":
                    return await self._get_categories()
                elif tool_name == "get_bestsellers":
                    return await self._get_bestsellers(db, parameters)
                elif tool_name == "get_customer":
                    return await self._get_customer(db, parameters)
                elif tool_name == "create_customer":
                    return await self._create_customer(db, parameters)
                elif tool_name == "get_order_status":
                    return await self._get_order_status(db, parameters)
                elif tool_name == "get_customer_orders":
                    return await self._get_customer_orders(db, parameters)
                elif tool_name == "create_order":
                    return await self._create_order(db, parameters)
                elif tool_name == "get_recommendations":
                    return await self._get_recommendations(db, parameters)
                elif tool_name == "get_conversation_history":
                    return await self._get_conversation_history(db, parameters)
                else:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' not implemented"
                    }

            except Exception as e:
                logger.error(f"❌ Error executing tool {tool_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    async def _search_products(self, db: AsyncSession, params: Dict) -> Dict:
        """Search products"""
        query = params.get("query", "")
        category = params.get("category")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        limit = params.get("limit", 10)

        if query:
            products = await product_service.search_products(db, query, limit)
        else:
            products = await product_service.get_all_products(
                db, category=category, min_price=min_price,
                max_price=max_price, limit=limit
            )

        return {
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products]
        }

    async def _get_product_details(self, db: AsyncSession, params: Dict) -> Dict:
        """Get product details"""
        product_id = params.get("product_id")
        product = await product_service.get_product_by_id(db, product_id)

        if not product:
            return {
                "success": False,
                "error": f"Product {product_id} not found"
            }

        return {
            "success": True,
            "product": product.to_dict()
        }

    async def _check_stock(self, db: AsyncSession, params: Dict) -> Dict:
        """Check product stock"""
        product_id = params.get("product_id")
        quantity = params.get("quantity", 1)

        result = await product_service.check_stock(db, product_id, quantity)
        return {
            "success": True,
            "stock": result
        }

    async def _get_categories(self) -> Dict:
        """Get product categories"""
        categories = await product_service.get_categories()
        return {
            "success": True,
            "categories": categories
        }

    async def _get_bestsellers(self, db: AsyncSession, params: Dict) -> Dict:
        """Get bestselling products"""
        limit = params.get("limit", 5)
        products = await product_service.get_bestsellers(db, limit)

        return {
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products]
        }

    async def _get_customer(self, db: AsyncSession, params: Dict) -> Dict:
        """Get customer information"""
        phone = params.get("phone")
        email = params.get("email")

        customer = None
        if phone:
            customer = await customer_service.get_customer_by_phone(db, phone)
        elif email:
            customer = await customer_service.get_customer_by_email(db, email)

        if not customer:
            return {
                "success": False,
                "error": "Customer not found"
            }

        return {
            "success": True,
            "customer": customer.to_dict()
        }

    async def _create_customer(self, db: AsyncSession, params: Dict) -> Dict:
        """Create or update customer"""
        customer = await customer_service.create_or_update_customer(
            db,
            phone_number=params.get("phone"),
            name=params.get("name"),
            email=params.get("email"),
            address=params.get("address"),
            city=params.get("city"),
            preferred_channel=params.get("preferred_channel", "whatsapp")
        )

        return {
            "success": True,
            "customer": customer.to_dict(),
            "message": "Customer created/updated successfully"
        }

    async def _get_order_status(self, db: AsyncSession, params: Dict) -> Dict:
        """Get order status"""
        order_number = params.get("order_number")
        order = await order_service.get_order_by_number(db, order_number)

        if not order:
            return {
                "success": False,
                "error": f"Order {order_number} not found"
            }

        return {
            "success": True,
            "order": order.to_dict()
        }

    async def _get_customer_orders(self, db: AsyncSession, params: Dict) -> Dict:
        """Get customer orders"""
        phone = params.get("phone")
        limit = params.get("limit", 10)

        customer = await customer_service.get_customer_by_phone(db, phone)
        if not customer:
            return {
                "success": False,
                "error": "Customer not found"
            }

        orders = await order_service.get_customer_orders(db, customer.id, limit=limit)

        return {
            "success": True,
            "count": len(orders),
            "orders": [o.to_dict() for o in orders]
        }

    async def _create_order(self, db: AsyncSession, params: Dict) -> Dict:
        """Create new order"""
        # Get or create customer
        customer = await customer_service.create_or_update_customer(
            db,
            phone_number=params.get("customer_phone"),
            name=params.get("customer_name")
        )

        # Create order
        try:
            order = await order_service.create_order(
                db,
                customer_id=customer.id,
                products_data=params.get("products"),
                address=params.get("address"),
                city=params.get("city"),
                payment_method=params.get("payment_method"),
                channel=params.get("channel", "web")
            )

            return {
                "success": True,
                "order": order.to_dict(),
                "message": f"Order {order.order_number} created successfully"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_recommendations(self, db: AsyncSession, params: Dict) -> Dict:
        """Get product recommendations"""
        preferences = params.get("preferences")
        limit = params.get("limit", 5)

        from app.services.agent_service import agent_service
        recommendations = await agent_service.get_recommendations(db, preferences)

        return {
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations
        }

    async def _get_conversation_history(self, db: AsyncSession, params: Dict) -> Dict:
        """Get conversation history"""
        phone = params.get("phone")
        limit = params.get("limit", 10)

        conversations = await conversation_service.get_conversation_history(
            db, phone_number=phone, limit=limit
        )

        return {
            "success": True,
            "count": len(conversations),
            "conversations": [c.to_dict() for c in conversations]
        }

    def list_tools(self) -> List[Dict]:
        """
        List all available tools

        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        Get information about a specific tool

        Args:
            tool_name: Name of the tool

        Returns:
            Tool definition or None
        """
        return self.tools.get(tool_name)


# Global MCP server instance
mcp_server = MCPServer()
