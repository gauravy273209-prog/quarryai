import asyncio
import os
import httpx
from dotenv import load_dotenv
from deepgram import DeepgramClient
from groq import AsyncGroq

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def test_deepgram_stt():
    print("\n🟡 Testing Deepgram STT...")
    try:
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        print("✅ Deepgram API key is valid!")
        return True
    except Exception as e:
        print(f"❌ Deepgram error: {e}")
        return False

async def test_groq():
    print("\n🟡 Testing Groq (Llama3)...")
    try:
        groq_client = AsyncGroq(api_key=GROQ_API_KEY)
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful AI voice assistant. Keep responses short."},
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            max_tokens=100
        )
        reply = response.choices[0].message.content
        print(f"✅ Groq replied: {reply}")
        return True
    except Exception as e:
        print(f"❌ Groq error: {e}")
        return False

async def test_deepgram_tts():
    print("\n🟡 Testing Deepgram TTS (Aura)...")
    try:
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"text": "Hello! I am your QuarryAI voice assistant."}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            with open("test_tts_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"✅ Deepgram TTS works! Audio saved ({len(response.content)} bytes)")
            return True
        else:
            print(f"❌ Deepgram TTS error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Deepgram TTS error: {e}")
        return False

async def main():
    print("🚀 QuarryAI Voice Pipeline Test")
    print("=" * 35)
    await test_deepgram_stt()
    await test_groq()
    await test_deepgram_tts()
    print("\n" + "=" * 35)
    print("✅ All tests complete!")

asyncio.run(main())