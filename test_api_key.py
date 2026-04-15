# test_api_key.py - Test your Gemini API key
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_NEW_gemini_api_key_here":
    print("❌ API key not configured!")
    print("\n📝 Steps to fix:")
    print("1. Rotate your exposed API key at: https://console.cloud.google.com/apis/credentials")
    print("2. Open .env file")
    print("3. Add your NEW key after: GEMINI_API_KEY=")
    print("4. Save and run this test again")
else:
    print("✅ API key loaded from .env")
    print(f"🔑 Key starts with: {api_key[:10]}...{api_key[-4:]}")

    # Test the API key
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        print("\n🧪 Testing API connection...")
        response = model.generate_content("Salaam! Please respond with 'API test successful' in Urdu.")
        print(f"✅ API Response: {response.text[:100]}...")
        print("\n✅ Your API key is working correctly!")

    except Exception as e:
        print(f"\n❌ API Error: {e}")
        print("\n📝 Possible issues:")
        print("- API key is invalid or expired")
        print("- Gemini API not enabled")
        print("- Network connectivity issue")
        print("\nCheck: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
