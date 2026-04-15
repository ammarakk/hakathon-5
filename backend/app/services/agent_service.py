"""
AI Agent service using PydanticAI + Gemini 2.0 Flash
"""

from typing import Optional, List, Dict
from app.services.product_service import product_service
from app.services.order_service import order_service
from app.services.customer_service import customer_service
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NurScentsAgent:
    """Nur Scents AI Customer Service Agent"""

    def __init__(self):
        """Initialize the agent with Gemini API"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""

        return """You are Nur Assistant, a helpful and polite AI customer service agent for Nur Scents.

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
- Closing: "Agar koi sawal ho to zaroor poochein. Allah Hafiz! 🌸"

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

Be helpful, friendly, and guide customers to the best products for their needs."""

    async def process_message(
        self,
        message: str,
        channel: str = "web",
        customer_context: Optional[Dict] = None,
        db: Optional[AsyncSession] = None,
    ) -> str:
        """
        Process a customer message through the AI agent

        Args:
            message: Customer message
            channel: Communication channel (whatsapp, email, web)
            customer_context: Customer information
            db: Database session

        Returns:
            Agent response
        """
        try:
            # Get channel-specific context
            channel_context = self._get_channel_context(channel)

            # Build context for the model
            context_parts = [
                self.system_prompt,
                f"\nCURRENT CHANNEL: {channel.upper()}",
                f"CHANNEL GUIDELINES: {channel_context}",
            ]

            # Add customer context if available
            if customer_context:
                context_parts.append(
                    f"\nCUSTOMER CONTEXT:"
                    f"\n- Name: {customer_context.get('name', 'Unknown')}"
                    f"\n- Previous Orders: {customer_context.get('total_orders', 0)}"
                    f"\n- Total Spent: PKR {customer_context.get('total_spent', 0)}"
                )

            context_parts.append(f"\nCUSTOMER MESSAGE: {message}")

            # Generate response
            full_prompt = "\n".join(context_parts)

            response = self.model.generate_content(full_prompt)
            response_text = response.text

            logger.info(f"🤖 AI Agent response generated for channel: {channel}")

            return response_text

        except Exception as e:
            logger.error(f"❌ Error processing message with AI agent: {e}")

            # Fallback response
            return self._get_fallback_response(channel)

    def _get_channel_context(self, channel: str) -> str:
        """Get channel-specific context"""

        contexts = {
            "whatsapp": "Use Roman Urdu, friendly tone, emojis allowed",
            "email": "Use formal English, professional tone, no emojis",
            "web": "Use mixed English/Roman Urdu, semi-formal tone, some emojis",
        }

        return contexts.get(channel, contexts["web"])

    def _get_fallback_response(self, channel: str) -> str:
        """Get fallback response in case of errors"""

        fallbacks = {
            "whatsapp": "Maaf kijiye, main abhi process kar raha hun. Thori der mein jawab doonga. JazakAllah!",
            "email": "We apologize for the inconvenience. Our system is processing your request and will respond shortly.",
            "web": "Sorry, we're processing your request. We'll respond shortly. Thank you for your patience!",
        }

        return fallbacks.get(channel, fallbacks["web"])

    async def should_escalate(
        self, message: str, conversation_history: List[Dict]
    ) -> tuple[bool, str]:
        """
        Determine if conversation should be escalated to owner

        Args:
            message: Current message
            conversation_history: Previous messages in conversation

        Returns:
            Tuple of (should_escalate, reason)
        """
        urgent_keywords = [
            "refund",
            "complaint",
            "fraud",
            "cheat",
            "scam",
            "police",
            "legal",
            "court",
            "lawyer",
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

    async def get_product_recommendations(
        self, db: AsyncSession, preferences: Optional[str] = None
    ) -> List[Dict]:
        """
        Get product recommendations based on preferences

        Args:
            db: Database session
            preferences: Customer preferences (optional)

        Returns:
            List of recommended products
        """
        try:
            if preferences:
                # Search products based on preferences
                products = await product_service.search_products(
                    db=db, query=preferences, limit=5
                )
            else:
                # Return bestsellers
                products = await product_service.get_bestsellers(db=db, limit=5)

            return [p.to_dict() for p in products]

        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return []


# Global agent instance
nur_scents_agent = NurScentsAgent()


class AgentService:
    """Service layer for agent operations"""

    def __init__(self):
        self.agent = nur_scents_agent

    async def process_customer_message(
        self,
        message: str,
        channel: str,
        customer_context: Optional[Dict] = None,
        db: Optional[AsyncSession] = None,
    ) -> str:
        """
        Process customer message through agent

        Args:
            message: Customer message
            channel: Communication channel
            customer_context: Customer information
            db: Database session

        Returns:
            Agent response
        """
        return await self.agent.process_message(
            message=message,
            channel=channel,
            customer_context=customer_context,
            db=db,
        )

    async def check_escalation(
        self, message: str, conversation_history: List[Dict]
    ) -> tuple[bool, str]:
        """
        Check if conversation should be escalated

        Args:
            message: Current message
            conversation_history: Previous messages

        Returns:
            Tuple of (should_escalate, reason)
        """
        return await self.agent.should_escalate(message, conversation_history)

    async def get_recommendations(
        self, db: AsyncSession, preferences: Optional[str] = None
    ) -> List[Dict]:
        """
        Get product recommendations

        Args:
            db: Database session
            preferences: Customer preferences

        Returns:
            List of recommended products
        """
        return await self.agent.get_product_recommendations(db, preferences)


# Global service instance
agent_service = AgentService()
