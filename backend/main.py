import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi import fastAPI, WebSocket, Request
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8000))
SYSTEM_MESSAGE = (
  "You are a helpful assistant that can help with a wide range of tasks. "
)

VOICE = 'alloy'

LOG_EVENT_TYPES = [
  'response.content.done', 'rate_limits.updated', 'response.done',
  'input_audio_buffer.committed', 'unput_audio_buffer.speech_stopped', 
  'input_audio_buffer.speech_started', 'session.created'
]
 
app = FastAPI()

if not OPENAI_API_KEY:
  raise ValueError("OPENAI_API_KEY is not set in the environment variables")

@app.get("/", response_class=JSONResponse)
async def index_page():
  return {"message": "Server is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  print("Client connected to the server")
  await websocket.accept()

  async with websockets.connect()
