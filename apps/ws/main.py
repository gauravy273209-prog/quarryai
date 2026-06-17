import os
import json
import base64
import asyncio
import httpx
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, Response
from dotenv import load_dotenv
from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.future import select
import uuid

load_dotenv()

app = FastAPI(title="QuarryAI Voice WebSocket Server")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_SYSTEM_PROMPT = """You are a helpful AI voice assistant for QuarryAI.
Keep your responses short, conversational, and under 2 sentences.
You are speaking on a phone call, so be natural and friendly."""

# ─── DB setup (minimal, just for agent lookup) ───────────────
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone_number = Column(String, nullable=True)
    system_prompt = Column(Text, nullable=True)
    voice_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

async def get_agent_by_phone(phone_number: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Agent).where(Agent.phone_number == phone_number, Agent.is_active == True)
        )
        return result.scalar_one_or_none()

# ─── Health check ─────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "quarryai-voice-ws"}

@app.get("/test")
async def test_page():
    with open("test_call.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# ─── Twilio webhook ───────────────────────────────────────────
@app.post("/twilio/voice")
async def twilio_voice(request: Request):
    host = request.headers.get("host")
    form = await request.form()
    to_number = form.get("To", "")

    # Look up agent by phone number
    agent = await get_agent_by_phone(to_number)
    agent_prompt = agent.system_prompt if agent and agent.system_prompt else ""

    # Pass prompt to WebSocket via query param (URL encoded)
    import urllib.parse
    encoded_prompt = urllib.parse.quote(agent_prompt)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{host}/ws/voice?prompt={encoded_prompt}" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

# ─── Deepgram STT ─────────────────────────────────────────────
async def transcribe_audio(audio_bytes: bytes) -> str:
    url = "https://api.deepgram.com/v1/listen?model=nova-2&language=en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/mulaw;rate=8000"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=audio_bytes)
    if response.status_code == 200:
        data = response.json()
        transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript.strip()
    return ""

# ─── Groq LLM ─────────────────────────────────────────────────
async def get_llm_reply(conversation_history: list, system_prompt: str) -> str:
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)
    response = await groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + conversation_history[-10:],
        max_tokens=150
    )
    return response.choices[0].message.content

# ─── Deepgram TTS ─────────────────────────────────────────────
async def synthesize_speech(text: str) -> bytes:
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"text": text})
    if response.status_code == 200:
       with open("debug_audio.raw", "wb") as f:
            f.write(response.content)
        print(f"🔍 Saved {len(response.content)} bytes to debug_audio.raw")
        return response.content
    return b""

# ─── Main WebSocket ───────────────────────────────────────────
@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket, prompt: str = ""):
    await websocket.accept()
    print("📞 New call connected")

    import urllib.parse
    decoded_prompt = urllib.parse.unquote(prompt)
    system_prompt = decoded_prompt if decoded_prompt.strip() else DEFAULT_SYSTEM_PROMPT
    print(f"🤖 Using system prompt: {system_prompt[:80]}...")

    conversation_history = []
    audio_buffer = bytearray()
    stream_sid = None

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                print(f"🎙️ Stream started: {stream_sid}")
                greeting = "Hello! Thank you for calling. How can I help you today?"
                audio = await synthesize_speech(greeting)
                if audio:
                    payload = base64.b64encode(audio).decode("utf-8")
                    await websocket.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": payload}
                    })

            elif event == "media":
                chunk = base64.b64decode(data["media"]["payload"])
                audio_buffer.extend(chunk)

                if len(audio_buffer) >= 16000:
                    audio_data = bytes(audio_buffer)
                    audio_buffer.clear()

                    transcript = await transcribe_audio(audio_data)
                    if transcript:
                        print(f"👤 User said: {transcript}")
                        conversation_history.append({"role": "user", "content": transcript})

                        reply = await get_llm_reply(conversation_history, system_prompt)
                        print(f"🤖 AI reply: {reply}")
                        conversation_history.append({"role": "assistant", "content": reply})

                        audio = await synthesize_speech(reply)
                        if audio and stream_sid:
                            payload = base64.b64encode(audio).decode("utf-8")
                            await websocket.send_json({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": payload}
                            })

            elif event == "stop":
                print("📴 Call ended")
                break

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        print("🔌 Connection closed")