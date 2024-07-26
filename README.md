# A DuckDuckGo AI chat client written in python

A python-implemented DuckDuckGo AI chat client with model selection and dialog history during usage. 

> Based on the ideas of [duck-hey](https://github.com/b1ek/hey)

## Disclaimer
By using this client you accept [DuckDuckGo AI Chat ToS](https://duckduckgo.com/aichat/privacy-terms)


## Installation
1. Install [python 3.12](https://www.python.org/downloads/)

2. Create python venv (optionally)

 ```bash
 python -m venv .venv && source .venv/bin/activate
 ```

3. Install package

   - Install auto
   ```bash
   pip install -U https://github.com/mrgick/duckduckgo-chat-ai/archive/master.zip
   ```
   - Install manually
     1. Clone repo

       ```bash
       git clone https://github.com/mrgick/duckduckgo-chat-ai.git && cd duckduckgo-chat-ai
       ```
     2. Install package

       ```bash
       pip install -U .
       ```

## Usage
- Using terminal
```bash
python -m duck_chat
```
or
```
duck_chat
```

> P.S. You can use hey config ```".config/hey/conf.toml"``` Thanks [k-aito](https://github.com/mrgick/duckduckgo-chat-ai/pull/1)


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
