#!/usr/bin/env python3
"""Test AI directly to see if rate limiting is the issue"""
import os
import sys
import asyncio

sys.path.insert(0, os.getcwd())

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

print("=" * 60)
print("TESTING GEMINI AI DIRECTLY")
print("=" * 60)
print()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

async def test_ai():
    try:
        # Try to create agent and run
        model = GoogleModel("gemini-2.5-flash")
        agent = Agent(model, system_prompt="You are a helpful assistant for Nur Scents perfume business in Pakistan. Oudh Attar 6ml costs PKR 4,500 and 3ml costs PKR 2,500.")

        print("Testing simple query...")
        print("-" * 60)

        result = await agent.run("What is the price of Oudh Attar? Answer in Roman Urdu.")

        print(f"[SUCCESS] AI Response:")
        print(result.output)
        print()
        print("=" * 60)
        print("AI IS WORKING!")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] {e}")
        print()

        error_str = str(e)
        if "429" in error_str:
            print("ISSUE: Rate Limiting")
            print()
            print("SOLUTION:")
            print("1. Wait 5-10 minutes")
            print("2. Or get new API key from: https://ai.google.dev/")
            print()
        elif "quota" in error_str.lower():
            print("ISSUE: Quota Exceeded")
            print()
            print("SOLUTION:")
            print("1. Wait 24 hours for quota reset")
            print("2. Or upgrade to paid plan")
            print()
        else:
            print("ISSUE: Unknown Error")
            print()

if __name__ == "__main__":
    asyncio.run(test_ai())

print()
