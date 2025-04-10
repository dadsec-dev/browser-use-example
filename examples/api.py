from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from AmazonShoppingAssistant import kickStartBrowser
import asyncio
import logging

# Set up logging
logging.getLogger('browser_use').setLevel(logging.DEBUG)

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

@app.post("/browse")
async def browse_website(request: TaskRequest):
    try:
        task = request.task
        print(f"This is task from the API: {task} ============")
        result = await kickStartBrowser(task)

        print(f"This is result from the Automation: {result}")
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 