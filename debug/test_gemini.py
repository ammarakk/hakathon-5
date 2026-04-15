# debug/test_gemini.py
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def test_models():
    from pydantic_ai import Agent

    models_to_test = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("GEMINI_API_KEY not set!")
        return

    print(f"API Key: {api_key[:8]}...\n")

    for model_name in models_to_test:
        try:
            print(f"Testing {model_name}...")
            agent = Agent(
                model=model_name,
                system_prompt="You are a helpful assistant for Nur Scents perfume shop in Karachi. Reply in friendly Pakistani English with Islamic greetings."
            )
            result = await agent.run(
                "bhai oud attar ka price kya hai?"
            )
            print(f"{model_name} WORKING")
            print(f"Response: {result.data[:100]}...")
            print(f"USE THIS MODEL: {model_name}\n")
            break
        except Exception as e:
            print(f"{model_name} failed: {str(e)[:80]}")
            print()

asyncio.run(test_models())
