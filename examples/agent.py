from typing import Optional, Callable, Awaitable
from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult
from langchain_openai import ChatOpenAI
import asyncio
import logging
from datetime import datetime

logging.getLogger('browser_use').setLevel(logging.DEBUG)

async def kickStartBrowser(
    task: str,
    update_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    model: str = "gpt-3.5-turbo"
):
    print("browser initializing ================")
    browser = Browser(config=BrowserConfig(headless=True, disable_security=True))
    print("browser successfully initialized ================")
    llm = ChatOpenAI(model=model, temperature=0.0)
    print("llm initialized ================")
    
    # Parse task parameters using LLM
    parse_prompt = f"""
    Extract the following parameters from the task description as integers in seconds. If not specified, return 'None':
    - Interval: How often to check (e.g., 'every 30 minutes' -> 1800).
    - Max time: Maximum monitoring duration (e.g., 'for up to 3 days' -> 259200).
    - Update frequency: How often to send periodic updates (e.g., 'send updates every hour' -> 3600).
    Respond in this format: {{'interval': value, 'max_time': value, 'update_frequency': value}}
    Task: {task}
    """
    params_str = await llm.apredict(parse_prompt)
    try:
        params = eval(params_str)  # Safely parse the dictionary; in production, use json.loads
        interval = params.get('interval')
        max_time = params.get('max_time')
        update_frequency = params.get('update_frequency')
    except Exception:
        interval, max_time, update_frequency = None, None, None

    # Create controller
    controller = Controller()
    
    # Register send_update action
    @controller.action('Send update')
    async def send_update(message: str):
        print(f"Sending update: {message}")
        if update_callback:
            await update_callback(message)
        return ActionResult(extracted_content=f"Update sent: {message}")
    
    # Register wait action
    @controller.action('Wait')
    async def wait(duration: int):
        await asyncio.sleep(duration)
        return ActionResult(extracted_content=f"Waited for {duration} seconds")

    # Enhanced system prompt
    custom_system_prompt = f"""
    You are an AI agent designed to automate browser tasks and run in the background for prolonged monitoring and interval-based tasks.
    Your goal is to accomplish the task efficiently.

    **Rules:**
    - After extracting content or completing significant actions, invoke 'Send update' with a relevant message.
    - For monitoring tasks:
      - Use the 'Wait' action to pause for a specified duration (in seconds) before the next action.
      - Check the status at intervals as specified (e.g., 'Wait 1800' for 30 minutes).
      - Send periodic updates as requested or every few checks if not specified.
      - Stop when the condition is met (e.g., status changes) or instructed.
    - Send an initial 'Task started' update when beginning.
    - Use the current time (provided) to decide when to send periodic updates.
    - Structure updates clearly and consistently.

    Current time will be provided before each decision.
    """
    
    agent = Agent(
        task=task,
        llm=llm,
        use_vision=False,
        browser=browser,
        controller=controller,
        message_context=custom_system_prompt
    )
    
    try:
        print("preparing to run agent ================")
        if max_time is not None:
            result = await asyncio.wait_for(agent.run(), timeout=max_time)
        else:
            result = await agent.run()
    except asyncio.TimeoutError:
        if update_callback:
            await update_callback("Monitoring timed out.")
        result = "Monitoring timed out."
    finally:
        await browser.close()
    
    return result