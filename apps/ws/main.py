import os
import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from dotenv import load_dotenv
from openai import AsyncOpenAI
import httpx

load_dotenv()

app = FastAPI(title="QuarryAI Voice Service")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "quarryai-voice"}

@app.post("/twilio/incoming")
async def twilio_incoming(request: Request):
    """Twilio calls this when someone calls your number"""
    host = request.headers.get("host")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{host}/ws/voice" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """Main voice pipeline: Twilio audio → Deepgram STT → OpenAI → ElevenLabs TTS → Twilio"""
    await websocket.accept()
    print("📞 Call connected")
    
    stream_sid = None
    conversation_history = []
    audio_buffer = b""

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                print(f"🎙️ Stream started: {stream_sid}")
                # Greet the caller
                greeting = "Hello! I'm an AI assistant. How can I help you today?"
                audio = await text_to_speech(greeting)
                if audio:
                    await send_audio_to_twilio(websocket, audio, stream_sid)
                conversation_history.append({"role": "assistant", "content": greeting})

            elif event == "media":
                # Collect audio chunks
                payload = data["media"]["payload"]
                audio_buffer += base64.b64decode(payload)
                
                # Process every ~2 seconds of audio (16000 bytes at 8kHz mulaw)
                if len(audio_buffer) >= 16000:
                    transcript = await speech_to_text(audio_buffer)
                    audio_buffer = b""
                    
                    if transcript and len(transcript.strip()) > 2:
                        print(f"👤 Caller said: {transcript}")
                        conversation_history.append({"role": "user", "content": transcript})
                        
                        # Get AI response
                        reply = await get_ai_response(conversation_history)
                        print(f"🤖 AI replied: {reply}")
                        conversation_history.append({"role": "assistant", "content": reply})
                        
                        # Convert to speech and send back
                        audio = await text_to_speech(reply)
                        if audio and stream_sid:
                            await send_audio_to_twilio(websocket, audio, stream_sid)

            elif event == "stop":
                print("📵 Call ended")
                break

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔌 WebSocket closed")


async def speech_to_text(audio_data: bytes) -> str:
    """Send audio to Deepgram and get transcript"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen?model=nova-2&encoding=mulaw&sample_rate=8000",
                headers={
                    "Authorization": f"Token {DEEPGRAM_API_KEY}",
                    "Content-Type": "audio/mulaw",
                },
                content=audio_data,
                timeout=10.0
            )
            result = response.json()
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            return transcript
    except Exception as e:
        print(f"STT error: {e}")
        return ""


async def get_ai_response(conversation_history: list) -> str:
    """Send conversation to OpenAI and get response"""
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI voice assistant. Keep responses short and conversational — 1-2 sentences max since this is a phone call."},
                *conversation_history
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
        return "I'm sorry, I didn't catch that. Could you repeat?"


async def text_to_speech(text: str) -> bytes:
    """Convert text to speech using ElevenLabs, return mulaw audio for Twilio"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/stream",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2",
                    "output_format": "ulaw_8000",
                },
                timeout=15.0
            )
            return response.content
    except Exception as e:
        print(f"TTS error: {e}")
        return b""


async def send_audio_to_twilio(websocket: WebSocket, audio: bytes, stream_sid: str):
    """Send audio back to Twilio over WebSocket"""
    encoded = base64.b64encode(audio).decode("utf-8")
    await websocket.send_text(json.dumps({
        "event": "media",
        "streamSid": stream_sid,
        "media": {"payload": encoded}
    }))