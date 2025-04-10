from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from AmazonShoppingAssistant import kickStartBrowser
import asyncio
import uuid

app = FastAPI()
active_connections = {}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Change this to your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS etc
    allow_headers=["*"],  # allow all headers
)
class TaskRequest(BaseModel):
    task: str

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            await websocket.send_text(f"task monitoring in progress {client_id}")
            await asyncio.sleep(7)  # Keeps connection alive
            # await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.pop(client_id, None)
@app.post("/browse")
async def browse_website(request: TaskRequest):
    print(f"taks started {request.task}")
    task = request.task
    task_id = str(uuid.uuid4())
    asyncio.create_task(run_monitor(task_id, task))
    return {"message": "Monitoring started", "task_id": task_id}

async def run_monitor(task_id, task):
    print("new task created")
    try:
        # Send initial update
        await send_update(task_id, "👀 Monitoring with GPT-3.5...")
        
        # Pass a callback function to send updates via WebSocket
        low_result = await kickStartBrowser(task, lambda msg: asyncio.create_task(send_update(task_id, msg)), model="gpt-3.5-turbo")
        
        # Log low result and send it to the WebSocket
        print("low_result:::", low_result)
        
        if "done" in low_result.lower() or "found" in low_result.lower():
            await send_update(task_id, "🔍 Escalating to GPT-4o for validation...")
            final_result = await kickStartBrowser(task, lambda msg: asyncio.create_task(send_update(task_id, msg)), model="gpt-4o")
            await send_update(task_id, f"✅ Final result: {final_result}")
        else:
            await send_update(task_id, f"✅ No significant changes: {low_result}")

    except Exception as e:
        await send_update(task_id, f"❌ Error: {str(e)}")
    finally:
        await send_update(task_id, "💀 Monitoring session ended.")


async def send_update(task_id: str, message: str):
    ws = active_connections.get(task_id)
    if ws:
        await ws.send_text(message)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 