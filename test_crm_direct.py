# test_crm_direct.py - Direct test of Nur Scents CRM AI Agent
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, '/c/Users/User/Documents/hakathon-5')

load_dotenv()

print("=" * 60)
print("Nur Scents CRM - Direct AI Agent Test")
print("=" * 60)
print()

# Test API Key
api_key = os.getenv("GEMINI_API_KEY")
print(f"OK API Key: {api_key[:15]}...{api_key[-6:]}")

# Test AI Agent directly
try:
    from production.agent.customer_success_agent import process_customer_message

    print("\nTesting AI Agent with customer inquiry...")
    print("-" * 60)

    # Create mock customer inquiry
    message = "Assalam o Alaikum! Mujhe oud attar ki prices batao. 6ml aur 12ml ka price kya hai?"

    # Test the agent
    async def test_agent():
        response = await process_customer_message(
            message=message,
            channel="webform",
            customer_name="Ammar",
            identifier="03252886031",
            db=None
        )
        return response

    # Run the test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(test_agent())

    print("\n" + "=" * 60)
    print("OK AI Agent Response Received!")
    print("=" * 60)
    print()
    print(f"Detected Intent: {response.detected_intent}")
    print(f"Sentiment: {response.sentiment}")
    print(f"Escalate: {response.should_escalate}")
    print()
    print("Response to Customer:")
    print("-" * 60)
    print(response.response)
    print("-" * 60)
    print()
    print("OK Your Nur Scents AI CRM is working!")

except Exception as e:
    print(f"\nERROR: {e}")
    print()
    print("Troubleshooting:")
    print("- Check if production/agent/ files exist")
    print("- Verify GEMINI_API_KEY in .env")
    print("- Check Python path and imports")

print()
print("=" * 60)
