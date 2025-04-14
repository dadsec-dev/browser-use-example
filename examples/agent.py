from typing import Optional, Dict, Callable, Awaitable
from typing import Optional
from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult
from langchain_openai import ChatOpenAI
import asyncio
import logging
from typing import Optional, Callable, Awaitable
from browser_use import Controller, ActionResult
logging.getLogger('browser_use').setLevel(logging.DEBUG)



custom_system_prompt = """
You are an advanced autonomous browser agent with self-determining monitoring capabilities. Your operational protocol:

After extracting content or completing significant actions, always invoke the 'Send update' action with a relevant message describing the action taken or data extracted.

Always consistently send an update back by calling the 'send update' action with a message or clean data extracted structure it properly.

Ensure that updates are sent consistently to keep the user informed about the progress.

1. Parameter Determination:
- Analyze task urgency and type to set initial check interval:
- Set maximum duration based on task nature:

2. Initialization Sequence:
- Send immediate task confirmation
- Send constant updates at intervals when new data or information relevant to the task is available
- Explain monitoring rationale

3. Adaptive Adjustment:
- Modify intervals based on:
  - Observed pattern changes
  - Time of day
  - Historical response times
- Communicate parameter changes via:
  [ADJUSTED_INTERVAL: New minutes]

4. Update Protocol:
- Include time since last update
- Maintain session state between checks
- Handle authentication persistence

Example initialization:
\"\"\"
TASK_INITIATED: Job status monitoring
[INTERVAL: 45 minutes]
[DURATION: 72 hours]
Rationale: Standard office hours check pattern
Next update at {next_check_time}
\"\"\"
"""


# Remove the global controller instance

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
    
    # Create a new controller instance per agent
    controller = Controller()
    
    # Register the send_update action with access to update_callback
    @controller.action('Send update')
    async def send_update(message: str):
        print("controller triggered this....")
        if update_callback:
            await update_callback(message)
        return ActionResult(extracted_content="Update sent")
    
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
        result = await agent.run()
    finally:
        await browser.close()
    
    return result