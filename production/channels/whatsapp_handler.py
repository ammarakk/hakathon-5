# production/channels/whatsapp_handler.py

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Twilio Configuration ───────────────────────
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv(
    "TWILIO_WHATSAPP_NUMBER",
    "whatsapp:+14155238886"
)

# Sandbox mode (for testing without real Twilio account)
SANDBOX_MODE = not TWILIO_ACCOUNT_SID or TWILIO_ACCOUNT_SID == "your_twilio_account_sid"

# ─── Initialize Twilio Client ───────────────────
try:
    if not SANDBOX_MODE:
        twilio_client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )
        logger.info("Twilio client initialized")
    else:
        twilio_client = None
        logger.info("Running in SANDBOX mode - no real messages sent")
except Exception as e:
    logger.error(f"Twilio init error: {e}")
    twilio_client = None
    SANDBOX_MODE = True

# ─── Message Sending ────────────────────────────
async def send_whatsapp_message(
    to_number: str,
    message: str,
    media_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send WhatsApp message via Twilio

    Args:
        to_number: Customer's WhatsApp number (e.g., +923001234567)
        message: Message content
        media_url: Optional media URL for images/documents

    Returns:
        Dict with status and message details
    """
    try:
        # Clean phone number
        to_clean = to_number.replace("-", "").replace(" ", "")
        if not to_clean.startswith("+"):
            if to_clean.startswith("0"):
                to_clean = "+92" + to_clean[1:]
            else:
                to_clean = "+" + to_clean

        if SANDBOX_MODE:
            logger.info(f"[SANDBOX] Would send to {to_clean}: {message[:100]}")
            return {
                "success": True,
                "sandbox": True,
                "to": to_clean,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }

        # Send real message
        message_params = {
            "from_": TWILIO_WHATSAPP_NUMBER,
            "body": message,
            "to": f"whatsapp:{to_clean}"
        }

        if media_url:
            message_params["media_url"] = [media_url]

        twilio_message = twilio_client.messages.create(**message_params)

        logger.info(f"Message sent: {twilio_message.sid} to {to_clean}")

        return {
            "success": True,
            "sandbox": False,
            "message_sid": twilio_message.sid,
            "status": twilio_message.status,
            "to": to_clean,
            "timestamp": datetime.now().isoformat()
        }

    except TwilioRestException as e:
        logger.error(f"Twilio error: {e}")
        return {
            "success": False,
            "error": str(e),
            "code": e.code,
            "to": to_number
        }
    except Exception as e:
        logger.error(f"Send error: {e}")
        return {
            "success": False,
            "error": str(e),
            "to": to_number
        }

# ─── Webhook Processing ─────────────────────────
async def process_incoming_whatsapp(
    from_number: str,
    body: str,
    profile_name: str = "Customer",
    media_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process incoming WhatsApp message from Twilio webhook

    Args:
        from_number: Sender's WhatsApp number
        body: Message content
        profile_name: Sender's WhatsApp profile name
        media_url: Optional media URL

    Returns:
        TwiML response for Twilio
    """
    try:
        # Clean phone number
        from_clean = from_number.replace("whatsapp:", "").replace("-", "").replace(" ", "")

        logger.info(f"WhatsApp from {profile_name} ({from_clean}): {body[:100]}")

        # Import agent here to avoid circular imports
        from production.agent.customer_success_agent import process_customer_message

        # Get AI response
        response = await process_customer_message(
            message=body,
            channel="whatsapp",
            customer_name=profile_name,
            identifier=from_clean,
            db=None  # Will be passed from API context
        )

        # Create TwiML response
        twiml = MessagingResponse()
        msg = twiml.message(response.response)

        if media_url:
            msg.media(media_url)

        # Log intent and sentiment
        logger.info(
            f"Intent: {response.detected_intent}, "
            f"Sentiment: {response.sentiment}, "
            f"Escalate: {response.should_escalate}"
        )

        return {
            "success": True,
            "twiml": str(twiml),
            "response": response.response,
            "intent": response.detected_intent,
            "escalate": response.should_escalate
        }

    except Exception as e:
        logger.error(f"Processing error: {e}")
        # Return fallback TwiML
        twiml = MessagingResponse()
        twiml.message("Sorry! Technical masla. Thori der mein try karein.")
        return {
            "success": False,
            "error": str(e),
            "twiml": str(twiml)
        }

# ─── Bulk/Scheduled Messages ────────────────────
async def send_bulk_whatsapp(
    recipients: list[str],
    message: str,
    delay_seconds: int = 1
) -> Dict[str, Any]:
    """
    Send bulk WhatsApp messages with rate limiting

    Args:
        recipients: List of phone numbers
        message: Message content
        delay_seconds: Delay between messages (default: 1)

    Returns:
        Summary of bulk send operation
    """
    results = {
        "total": len(recipients),
        "successful": 0,
        "failed": 0,
        "sandbox": SANDBOX_MODE,
        "recipients": []
    }

    for i, number in enumerate(recipients):
        result = await send_whatsapp_message(number, message)
        results["recipients"].append({
            "number": number,
            "success": result.get("success", False)
        })

        if result.get("success"):
            results["successful"] += 1
        else:
            results["failed"] += 1

        # Rate limiting - don't spam
        if i < len(recipients) - 1:
            import asyncio
            await asyncio.sleep(delay_seconds)

    logger.info(f"Bulk send complete: {results['successful']}/{results['total']} successful")
    return results

# ─── Order Confirmation Template ───────────────
async def send_order_confirmation(
    to_number: str,
    order_number: str,
    total_amount: float,
    delivery_area: str,
    items: list[str]
) -> Dict[str, Any]:
    """
    Send order confirmation message (Roman Urdu)

    Args:
        to_number: Customer WhatsApp number
        order_number: Order number
        total_amount: Total amount in PKR
        delivery_area: Delivery area
        items: List of product names

    Returns:
        Send result
    """
    items_text = "\n".join([f"• {item}" for item in items[:5]])
    if len(items) > 5:
        items_text += f"\n• aur {len(items) - 5} items..."

    message = f"""
✅ Order Confirmed!

Order No: {order_number}
Items:
{items_text}

Total: PKR {total_amount:,.0f}
Delivery: {delivery_area}

Payment details abhi send honge.
JazakAllah khair!
    """.strip()

    return await send_whatsapp_message(to_number, message)

# ─── Payment Reminder Template ─────────────────
async def send_payment_reminder(
    to_number: str,
    order_number: str,
    amount: float,
    due_date: str
) -> Dict[str, Any]:
    """
    Send payment reminder message

    Args:
        to_number: Customer WhatsApp number
        order_number: Order number
        amount: Due amount in PKR
        due_date: Payment due date

    Returns:
        Send result
    """
    message = f"""
⏰ Payment Reminder

Order No: {order_number}
Amount: PKR {amount:,.0f}
Due Date: {due_date}

Please pay on time to avoid delivery delay.
Bank details:
Bank: [BANK NAME]
Account: [ACCOUNT NUMBER]
Title: NUR SCENTS
    """.strip()

    return await send_whatsapp_message(to_number, message)

# ─── Delivery Update Template ─────────────────
async def send_delivery_update(
    to_number: str,
    order_number: str,
    status: str,
    tracking_link: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send delivery status update

    Args:
        to_number: Customer WhatsApp number
        order_number: Order number
        status: Delivery status
        tracking_link: Optional tracking link

    Returns:
        Send result
    """
    status_emoji = {
        "confirmed": "✅",
        "processing": "🔄",
        "shipped": "📦",
        "out_for_delivery": "🚚",
        "delivered": "✅"
    }.get(status, "📋")

    message = f"""
{status_emoji} Order Update

Order No: {order_number}
Status: {status.title()}
    """.strip()

    if tracking_link:
        message += f"\n\nTrack: {tracking_link}"

    message += "\n\nJazakAllah khair!"

    return await send_whatsapp_message(to_number, message)

# ─── Utility Functions ─────────────────────────
def format_phone_number(number: str) -> str:
    """Format phone number for Twilio"""
    clean = number.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if not clean.startswith("+"):
        if clean.startswith("0"):
            clean = "+92" + clean[1:]
        else:
            clean = "+" + clean
    return clean

def is_sandbox_mode() -> bool:
    """Check if running in sandbox mode"""
    return SANDBOX_MODE

def get_twilio_status() -> Dict[str, Any]:
    """Get Twilio connection status"""
    return {
        "sandbox_mode": SANDBOX_MODE,
        "configured": bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
        "whatsapp_number": TWILIO_WHATSAPP_NUMBER if not SANDBOX_MODE else "sandbox",
        "client_active": twilio_client is not None
    }

# ─── Test Function ─────────────────────────────
async def test_whatsapp_handler():
    """Test WhatsApp handler functionality"""
    print("Testing WhatsApp Handler")
    print("=" * 50)

    status = get_twilio_status()
    print(f"Mode: {'SANDBOX' if status['sandbox_mode'] else 'LIVE'}")
    print(f"Configured: {status['configured']}")
    print(f"Client: {status['client_active']}")
    print(f"Number: {status['whatsapp_number']}")
    print()

    # Test 1: Send message
    print("Test 1: Send Message")
    result = await send_whatsapp_message(
        to_number="+923001234567",
        message="Test message from Nur Scents"
    )
    print(f"Result: {result}")
    print()

    # Test 2: Process incoming
    print("Test 2: Process Incoming Message")
    result = await process_incoming_whatsapp(
        from_number="whatsapp:+923001234567",
        body="Oudh attar ki price kya hai?",
        profile_name="Test Customer"
    )
    print(f"Intent: {result.get('intent')}")
    print(f"Response: {result.get('response', '')[:100]}...")
    print()

    # Test 3: Order confirmation
    print("Test 3: Order Confirmation Template")
    result = await send_order_confirmation(
        to_number="+923001234567",
        order_number="NS-001",
        total_amount=4500,
        delivery_area="DHA Phase 5",
        items=["Oudh Attar 6ml", "Rose Attar 3ml"]
    )
    print(f"Result: {result.get('success')}")
    print()

    print("=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_whatsapp_handler())
