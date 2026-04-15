# test_available_models.py - Check available Gemini models
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    print("Checking available Gemini models...")
    print("-" * 60)

    # List available models
    models = genai.list_models()

    print("Available models:")
    for model in models:
        if 'flash' in model.name.lower() or 'gemini' in model.name.lower():
            print(f"  - {model.name}")

except Exception as e:
    print(f"Error: {e}")
