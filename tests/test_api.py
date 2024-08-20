import asyncio
import random

import pytest

from duck_chat import DuckChat, ModelType


@pytest.fixture
def random_math_question():
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    question = f"{num1} + {num2}?"
    answer = str(num1 + num2)
    return question, answer


@pytest.mark.asyncio
@pytest.mark.parametrize("model", list(ModelType))
async def test_get_dialog(model, random_math_question):
    question, answer = random_math_question
    async with DuckChat(model=model) as chat:
        result = await chat.ask_question(question)
        assert answer in result
        await asyncio.sleep(1)
        result2 = await chat.ask_question("Are you right?")
        assert len(result2) >= 1
        await asyncio.sleep(1)
        result3 = await chat.reask_question(1)
        assert answer in result3
        await asyncio.sleep(1)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", list(ModelType))
async def test_steam_dialog(model, random_math_question):
    question, answer = random_math_question
    async with DuckChat(model=model) as chat:
        result = "".join([message async for message in chat.ask_question_stream(question)])
        assert answer in result
        await asyncio.sleep(1)
        result2 = "".join([message async for message in chat.ask_question_stream("Are you right?")])
        assert len(result2) >= 1
        await asyncio.sleep(1)
        result3 = "".join([message async for message in chat.reask_question_stream(1)])
        assert answer in result3
        await asyncio.sleep(1)
