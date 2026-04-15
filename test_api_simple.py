# test_api_simple.py - Test Google API key (no emojis)
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key.startswith("your_"):
    print("ERROR API key not configured")
    print("Add your API key to .env file")
    exit(1)

print(f"OK API key loaded: {api_key[:15]}...{api_key[-6:]}")

# Test the API key
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    print("\nTesting API connection...")
    response = model.generate_content("Salaam! Please respond with 'API test successful'")
    print(f"OK API Response: {response.text[:100]}")
    print("\nOK Your API key is working!")

except Exception as e:
    print(f"\nERROR API Error: {e}")
    print("\nTroubleshooting:")
    print("- Check if Gemini API is enabled")
    print("- Verify API key is correct")
    print("- Check network connectivity")
    print("- Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
