from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
import asyncio
import logging
logging.getLogger('browser_use').setLevel(logging.DEBUG)


async def kickStartBrowser(task:str):
    print("Starting browser... ===============")
    # Configure the browser to run in headless mode
    browser = Browser(
        config=BrowserConfig(
            headless=True,
            disable_security=True
        )
    )
    print("Starting browser 222... ===============")
    # Initialize the model
    llm = ChatOpenAI(
        model='gpt-4o',
        temperature=0.0,
    )
    print("Starting llm 333... ===============")
    # task = """
    # go to https://engineer-oasis-jobs.lovable.app/ and list me the available Software Engineer roles in there
    # """

    # Create the agent with your configured browser
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    # Run the task
    result = await agent.run()
    print(result)
    # Close the browser
    await browser.close()
    print("Closing browser... ===============")
    return result

    # async def main():
    #     result = await agent.run()
    #     print(result)

    # if __name__ == '__main__':
    #     asyncio.run(main())

