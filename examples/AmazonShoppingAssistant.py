import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent

load_dotenv()

# Initialize the model
llm = ChatOpenAI(
	model='gpt-4o',
	temperature=0.0,
)
task = """

Go on Amazon and find me the best deal on a laptop that will be very good for ai engineering, give me the details and link to buy, then go and find me the latest ps5 action games and give me the details and link to buy in a draft.txt file.
Make sure you get the best deal and the latest games.

"""

agent = Agent(task=task, llm=llm)


async def main():
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())