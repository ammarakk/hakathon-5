"""
Enhanced Agent Service with MCP Tool Integration
"""

from typing import Optional, List, Dict
import json
import google.generativeai as genai
from app.core.config import settings
from app.mcp.server import mcp_server
import logging

logger = logging.getLogger(__name__)


class EnhancedNurScentsAgent:
    """
    Enhanced AI Agent with MCP Tool Integration

    This agent can dynamically call tools through the MCP server
    to interact with the Nur Scents system.
    """

    def __init__(self):
        """Initialize the enhanced agent"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.mcp_server = mcp_server

        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Get system prompt with tool descriptions"""

        tool_descriptions = "\n\nAVAILABLE TOOLS:\n"
        for tool_name, tool_info in self.mcp_server.tools.items():
            tool_descriptions += f"\n{tool_name}:\n"
            tool_descriptions += f"  Description: {tool_info['description']}\n"
            tool_descriptions += f"  Parameters: {json.dumps(tool_info['parameters'], indent=2)}\n"

        return f"""You are Nur Assistant, an AI customer service agent for Nur Scents perfumes.

BUSINESS: Nur Scents - Premium attar and fragrance brand in Karachi, Pakistan
OWNER: Ammar
CURRENCY: PKR (Pakistani Rupees)
DELIVERY: Karachi, Lahore, Islamabad, Rawalpindi
FREE DELIVERY: Above PKR 15,000
DELIVERY CHARGES: Karachi PKR 150, other cities PKR 250

{tool_descriptions}

INSTRUCTIONS:
1. Use tools to help customers with:
   - Finding products (search_products, get_bestsellers)
   - Getting product details (get_product_details)
   - Checking stock (check_stock)
   - Creating orders (create_order)
   - Checking order status (get_order_status)
   - Getting recommendations (get_recommendations)
   - Customer lookup (get_customer)

2. When you need information, call the appropriate tool
3. Always verify stock before creating orders
4. Provide clear, helpful responses
5. Use channel-appropriate language and tone

RESPONSE STYLE BY CHANNEL:
- WhatsApp: Roman Urdu, friendly, emojis (🌸💐✨)
- Email: Formal English, professional, no emojis
- Web: Mixed English/Roman Urdu, semi-formal, some emojis

ESCALATION: Escalate to owner if customer mentions: refund, complaint, fraud, legal

Be helpful, friendly, and guide customers to make informed choices."""

    async def process_message(
        self,
        message: str,
        channel: str = "web",
        customer_context: Optional[Dict] = None,
        enable_tools: bool = True,
    ) -> str:
        """
        Process customer message with optional tool use

        Args:
            message: Customer message
            channel: Communication channel
            customer_context: Customer information
            enable_tools: Whether to enable tool calling

        Returns:
            Agent response
        """
        try:
            # Build context
            context_parts = [self.system_prompt]

            if customer_context:
                context_parts.append(
                    f"\nCURRENT CUSTOMER:\n"
                    f"- Name: {customer_context.get('name', 'Unknown')}\n"
                    f"- Phone: {customer_context.get('phone_number', 'N/A')}\n"
                    f"- Previous Orders: {customer_context.get('total_orders', 0)}\n"
                    f"- Total Spent: PKR {customer_context.get('total_spent', 0)}"
                )

            context_parts.append(f"\nCHANNEL: {channel.upper()}")
            context_parts.append(f"\nCUSTOMER MESSAGE: {message}")

            if enable_tools:
                context_parts.append(
                    "\n\nIMPORTANT: You can use the available tools to help the customer. "
                    "When you need information, indicate which tool you want to use."
                )

            full_prompt = "\n".join(context_parts)

            # Generate response
            response = self.model.generate_content(full_prompt)
            response_text = response.text

            # Check if agent wants to use tools
            if enable_tools and self._should_use_tools(response_text):
                # Parse tool calls and execute them
                enhanced_response = await self._execute_tools_and_respond(
                    message, response_text, channel, customer_context
                )
                return enhanced_response

            logger.info(f"🤖 Enhanced agent response generated for channel: {channel}")

            return response_text

        except Exception as e:
            logger.error(f"❌ Error in enhanced agent: {e}")
            return self._get_fallback_response(channel)

    def _should_use_tools(self, response: str) -> bool:
        """Check if response indicates tool usage is needed"""
        tool_keywords = [
            "let me check",
            "let me search",
            "i'll look up",
            "let me find",
            "checking",
            "searching",
        ]
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in tool_keywords)

    async def _execute_tools_and_respond(
        self,
        original_message: str,
        initial_response: str,
        channel: str,
        customer_context: Optional[Dict],
    ) -> str:
        """
        Execute tools based on agent response and generate enhanced response

        Args:
            original_message: Original customer message
            initial_response: Initial agent response
            channel: Communication channel
            customer_context: Customer information

        Returns:
            Enhanced response with tool results
        """
        try:
            # Determine which tools to call based on message
            tools_to_call = self._determine_tools_to_call(original_message)

            tool_results = []
            for tool_name, params in tools_to_call:
                result = await self.mcp_server.call_tool(tool_name, params)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })

            # Generate enhanced response with tool results
            if tool_results:
                enhanced_prompt = f"""{initial_response}

TOOL RESULTS:
{json.dumps(tool_results, indent=2)}

Based on these results, provide a clear and helpful response to the customer.
Use the channel-appropriate style for {channel}."""

                enhanced_response = self.model.generate_content(enhanced_prompt)
                return enhanced_response.text

            return initial_response

        except Exception as e:
            logger.error(f"❌ Error executing tools: {e}")
            return initial_response

    def _determine_tools_to_call(self, message: str) -> List[tuple]:
        """
        Determine which tools to call based on message content

        Args:
            message: Customer message

        Returns:
            List of (tool_name, parameters) tuples
        """
        message_lower = message.lower()
        tools_to_call = []

        # Product search
        if any(word in message_lower for word in ["search", "find", "looking for", "show me"]):
            # Extract search query
            query = message  # In real implementation, use NLP to extract
            tools_to_call.append(("search_products", {"query": query, "limit": 5}))

        # Price/stock check
        elif any(word in message_lower for word in ["price", "cost", "how much", "stock", "available"]):
            # Extract product reference
            if "oudh" in message_lower:
                tools_to_call.append(("get_product_details", {"product_id": "NS-001"}))
            elif "musk" in message_lower:
                tools_to_call.append(("get_product_details", {"product_id": "NS-003"}))

        # Order status
        elif any(word in message_lower for word in ["order status", "my order", "track order"]):
            # Would extract order number in real implementation
            pass

        # Recommendations
        elif any(word in message_lower for word in ["recommend", "suggest", "best", "popular"]):
            tools_to_call.append(("get_bestsellers", {"limit": 5}))

        return tools_to_call

    def _get_fallback_response(self, channel: str) -> str:
        """Get fallback response"""
        fallbacks = {
            "whatsapp": "Maaf kijiye, main abhi process kar raha hun. Thori der mein jawab doonga. JazakAllah!",
            "email": "We apologize for the inconvenience. Our system is processing your request.",
            "web": "Sorry, we're processing your request. We'll respond shortly!",
        }
        return fallbacks.get(channel, fallbacks["web"])


class EnhancedAgentService:
    """Service for enhanced agent operations"""

    def __init__(self):
        self.agent = EnhancedNurScentsAgent()

    async def process_with_tools(
        self,
        message: str,
        channel: str,
        customer_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Process message with tool integration

        Args:
            message: Customer message
            channel: Communication channel
            customer_context: Customer information

        Returns:
            Response with tool usage information
        """
        response = await self.agent.process_message(
            message=message,
            channel=channel,
            customer_context=customer_context,
            enable_tools=True,
        )

        return {
            "success": True,
            "response": response,
            "tools_enabled": True,
        }

    async def get_available_tools(self) -> List[Dict]:
        """Get list of available MCP tools"""
        return self.agent.mcp_server.list_tools()

    async def call_tool_directly(
        self, tool_name: str, parameters: Dict
    ) -> Dict:
        """
        Call an MCP tool directly

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        return await self.agent.mcp_server.call_tool(tool_name, parameters)


# Global service instance
enhanced_agent_service = EnhancedAgentService()
