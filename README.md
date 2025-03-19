# AI Shopping Assistant 🤖

This project demonstrates a practical implementation of [browser-use](https://github.com/browser-use/browser-use), a powerful tool that connects AI agents with browser capabilities. 

## 🌐 What is browser-use?

Browser-use is the easiest way to connect your AI agents with the browser. It provides a seamless interface for AI agents to interact with web content, making it perfect for tasks that require web browsing and data gathering.

## 📋 Project Overview

This implementation uses browser-use to create an intelligent shopping assistant that:
- Searches Amazon for the best deals on AI engineering laptops
- Finds the latest PS5 action games
- Analyzes product specifications and reviews
- Compares prices and features
- Generates a curated list with product details and purchase links in a draft.txt file

## 🎯 Features

- Automated product research
- Price comparison
- Specification analysis
- Deal finding
- Structured output in draft.txt

## 🛠️ Technical Stack

- Python
- LangChain
- OpenAI GPT-4
- browser-use agent
- dotenv (for environment variable management)

## 🚀 Getting Started

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   ```
3. Install dependencies:
   ```bash
   pip install python-dotenv langchain-openai browser-use
   ```
4. Set up your environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```
5. Run the script:
   ```bash
   python task.py
   ```

## 📝 Note

Make sure to keep your API keys secure and never commit them to version control. The `.gitignore` file is configured to exclude sensitive information.

## 📄 License

This project is open-source and available under the MIT License. 