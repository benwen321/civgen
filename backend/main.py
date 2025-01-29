from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            data = await websocket.receive_bytes()  # Receive binary audio data
            print(f"Received audio chunk of size: {len(data)} bytes")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        print("WebSocket connection closed")
