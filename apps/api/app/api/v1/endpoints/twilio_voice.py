import asyncio
import base64
import json
import os
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Agent
from app.models.call import Call

router = APIRouter()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')


# ── TwiML incoming call handler ────────────────────────────────────────────────

@router.post('/voice')
async def incoming_call(request: Request, db: AsyncSession = Depends(get_db)):
    '''Twilio calls this when a call comes in. Returns TwiML that opens a media stream.'''
    form = await request.form()
    to_number = str(form.get('To', ''))
    call_sid = str(form.get('CallSid', ''))

    result = await db.execute(select(Agent).where(Agent.phone_number == to_number))
    agent = result.scalar_one_or_none()

    if not agent:
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Response><Say voice="alice">Sorry, this number is not configured. Goodbye.</Say><Hangup/></Response>'
        )
        return Response(content=twiml, media_type='application/xml')

    host = request.headers.get('x-forwarded-host') or request.headers.get('host') or 'api.quarryai.co.in'
    ws_url = f'wss://{host}/api/v1/twilio/stream/{agent.id}'

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}">
            <Parameter name="agent_id" value="{agent.id}"/>
            <Parameter name="call_sid" value="{call_sid}"/>
        </Stream>
    </Connect>
</Response>'''
    return Response(content=twiml, media_type='application/xml')


# ── WebSocket media stream ─────────────────────────────────────────────────────

@router.websocket('/stream/{agent_id}')
async def media_stream(websocket: WebSocket, agent_id: str, db: AsyncSession = Depends(get_db)):
    '''Twilio streams call audio here. We transcribe → LLM → TTS → send back.'''
    await websocket.accept()

    result = await db.execute(select(Agent).where(Agent.id == uuid.UUID(agent_id)))
    agent = result.scalar_one_or_none()
    system_prompt = (agent.system_prompt if agent and agent.system_prompt
                     else 'You are a helpful AI voice assistant. Be concise — this is a phone call, keep answers under 2 sentences.')

    conversation: list[dict] = [{'role': 'system', 'content': system_prompt}]
    transcript_log: list[dict] = []
    stream_sid: str | None = None
    audio_buffer = bytearray()
    started_at = datetime.now(timezone.utc)

    # Persist call record immediately
    call_record = Call(
        agent_id=uuid.UUID(agent_id),
        status='ongoing',
        transcript=json.dumps([]),
        started_at=started_at,
    )
    db.add(call_record)
    await db.commit()
    await db.refresh(call_record)

    try:
        async for raw in websocket.iter_text():
            msg = json.loads(raw)
            event = msg.get('event')

            if event == 'start':
                stream_sid = msg['start']['streamSid']
                call_record.stream_sid = stream_sid
                await db.commit()

                # Send greeting
                greeting = 'Hello! How can I help you today?'
                audio = await tts(greeting)
                if audio and stream_sid:
                    await stream_audio(websocket, stream_sid, audio)

            elif event == 'media':
                chunk = base64.b64decode(msg['media']['payload'])
                audio_buffer.extend(chunk)

                # Process every ~0.5 s of mu-law audio (4000 bytes ≈ 0.5 s at 8 kHz)
                if len(audio_buffer) >= 4000:
                    pcm = bytes(audio_buffer)
                    audio_buffer.clear()

                    text = await stt(pcm)
                    if text and len(text.strip()) > 2:
                        transcript_log.append({'role': 'user', 'content': text})
                        conversation.append({'role': 'user', 'content': text})

                        reply = await llm(conversation)
                        if reply:
                            conversation.append({'role': 'assistant', 'content': reply})
                            transcript_log.append({'role': 'assistant', 'content': reply})

                            audio = await tts(reply)
                            if audio and stream_sid:
                                await stream_audio(websocket, stream_sid, audio)

                            call_record.transcript = json.dumps(transcript_log)
                            await db.commit()

            elif event == 'stop':
                break

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        ended_at = datetime.now(timezone.utc)
        duration = int((ended_at - started_at).total_seconds())
        call_record.status = 'completed'
        call_record.ended_at = ended_at
        call_record.duration_seconds = duration
        call_record.transcript = json.dumps(transcript_log)
        await db.commit()


# ── Helpers ────────────────────────────────────────────────────────────────────

async def stt(audio_bytes: bytes) -> str:
    '''Deepgram STT — mu-law 8 kHz input.'''
    if not DEEPGRAM_API_KEY:
        return ''
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                'https://api.deepgram.com/v1/listen'
                '?model=nova-2&encoding=mulaw&sample_rate=8000&language=en&punctuate=true',
                headers={'Authorization': f'Token {DEEPGRAM_API_KEY}', 'Content-Type': 'audio/mulaw'},
                content=audio_bytes,
            )
            if r.status_code == 200:
                return (r.json()
                        .get('results', {})
                        .get('channels', [{}])[0]
                        .get('alternatives', [{}])[0]
                        .get('transcript', ''))
    except Exception:
        pass
    return ''


async def llm(messages: list[dict]) -> str:
    '''Groq LLaMA — fast inference.'''
    if not GROQ_API_KEY:
        return "I'm sorry, I'm having trouble right now. Please try again later."
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'},
                json={'model': 'llama-3.1-8b-instant', 'messages': messages, 'max_tokens': 120, 'temperature': 0.7},
            )
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
    except Exception:
        pass
    return ''


async def tts(text: str) -> bytes | None:
    '''Deepgram TTS — returns mu-law 8 kHz audio.'''
    if not DEEPGRAM_API_KEY or not text.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                'https://api.deepgram.com/v1/speak'
                '?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none',
                headers={'Authorization': f'Token {DEEPGRAM_API_KEY}', 'Content-Type': 'application/json'},
                json={'text': text},
            )
            if r.status_code == 200:
                return r.content
    except Exception:
        pass
    return None


async def stream_audio(websocket: WebSocket, stream_sid: str, audio_bytes: bytes) -> None:
    '''Send audio to Twilio in 20 ms chunks (160 bytes of mu-law at 8 kHz).'''
    chunk_size = 160
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i + chunk_size]
        await websocket.send_json({
            'event': 'media',
            'streamSid': stream_sid,
            'media': {'payload': base64.b64encode(chunk).decode()},
        })
        await asyncio.sleep(0.02)
