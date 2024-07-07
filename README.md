# A DuckDuckGo AI chat client written in python

A python-implemented DuckDuckGo AI chat client with model selection and dialog history during usage. 

> Based on the ideas of [duck-hey](https://github.com/b1ek/hey)

## Disclaimer
By using this client you accept [DuckDuckGo AI Chat ToS](https://duckduckgo.com/aichat/privacy-terms)


## Installation
1. Install [python 3.12](https://www.python.org/downloads/)
2. Clone repo
```bash
git clone https://github.com/mrgick/duckduckgo-chat-ai.git && cd duckduckgo-chat-ai
```
3. Create python venv
```bash
python -m venv .venv && source .venv/bin/activate
```
4. Install package
```bash
pip install .
```

## Usage
- Using terminal
```bash
python -m duck_chat
```
- Using as library
```py
import asyncio
from duck_chat import DuckChat

async def main():
    async with DuckChat() as chat:
        print(await chat.ask_question("2+2?"))
        await asyncio.sleep(1)
        print(await chat.ask_question("6+6?"))

asyncio.run(main())
```