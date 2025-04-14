from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from browser_use import Agent, Browser, BrowserConfig, AgentHistoryList
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid
from agent import kickStartBrowser

app = FastAPI()
active_connections = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    active_connections[task_id] = websocket
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_connections.pop(task_id, None)

@app.post("/browse")
async def browse_website(request: TaskRequest):
    task_id = str(uuid.uuid4())
    print("===task id=====", task_id)
    asyncio.create_task(run_monitor(task_id, request.task))
    return {"message": "Monitoring started", "task_id": task_id}

def summarize_history(history: AgentHistoryList) -> str:
    """Extract a string summary from an AgentHistoryList object."""
    if history.history:
        last_entry = history.history[-1]
        if last_entry.result:
            last_result = last_entry.result[-1]
            if last_result.extracted_content:
                return last_result.extracted_content
    return "Task completed with no specific result"

async def run_monitor(task_id: str, task: str):
    try:
        async def update_callback(msg: str):
            await send_update(task_id, msg)

        await send_update(task_id, "👀 Starting monitoring...")
        
        # First pass with GPT-3.5
        await send_update(task_id, "⚙️ Initial analysis with GPT-3.5...")
        low_result = await kickStartBrowser(
            task=task,
            update_callback=update_callback,
            model="gpt-3.5-turbo"
        )
        low_result_str = summarize_history(low_result) if isinstance(low_result, AgentHistoryList) else str(low_result)

        # Second pass with GPT-4 if needed
        if needs_deeper_analysis(low_result_str):
            await send_update(task_id, "🔍 Deep analysis with GPT-4...")
            final_result = await kickStartBrowser(
                task=task,
                update_callback=update_callback,
                model="gpt-4"
            )
            final_result_str = summarize_history(final_result) if isinstance(final_result, AgentHistoryList) else str(final_result)
            await send_update(task_id, f"✅ Final result: {final_result_str}")
        else:
            await send_update(task_id, f"✅ Analysis complete: {low_result_str}")

    except Exception as e:
        await send_update(task_id, f"❌ Error: {str(e)}")
    finally:
        await send_update(task_id, "🏁 Monitoring session ended")
        await close_connection(task_id)

async def send_update(task_id: str, message: str):
    if ws := active_connections.get(task_id):
        try:
            await ws.send_text(message)
        except WebSocketDisconnect:
            await close_connection(task_id)

async def close_connection(task_id: str):
    if ws := active_connections.pop(task_id, None):
        await ws.close()

def needs_deeper_analysis(result: str) -> bool:
    return "done" in result.lower() or "found" in result.lower()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)