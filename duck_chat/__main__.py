import asyncio
import re
import sys

from .api import DuckChat
from .config import ModelType

async def main():
    # Parsing input and define action variable to control the loop flow
    def parsing_input_and_action(user_input):
        if re.match("^/help", question):
            print("\033[1;4m>>> Command response:\033[0m", end="\n")
            print("\033[1;1m- /help         \033[0mDisplay the help message")
            print("\033[1;1m- /singleline   \033[0mEnable singleline mode, validate is done by <enter>")
            print("\033[1;1m- /multiline    \033[0mEnable multiline mode, validate is done by \\")
            print("\033[1;1m- /quit         \033[0mQuit")
            return "continue"
        if re.match("^/singleline", question):
            return "singleline"
        if re.match("^/multiline", question):
            return  "multiline"
        if re.match("^/quit", question):
            return "break"

    # How get user input
    # It can be updated if multiline is enabled
    def get_user_input():
        return input().strip()

    async with DuckChat(model=ModelType.read_model_from_conf()) as chat:
        print('Type \033[1;4m/help\033[0m to display the help')
        while True:
            try:
                print("\033[1;4m>>> User input:\033[0m", end="\n")

                question = get_user_input()
                action = parsing_input_and_action(question)
            except EOFError:
                sys.exit(0)

            if action == "break":
                break
            elif action == "continue":
                continue
            elif action == "singleline":
                def get_user_input():
                    return input()
            elif action == "multiline":
                def get_user_input():
                    lines = []
                    while True:
                        line = input().strip()
                        lines.append(line)
                        if line.endswith("\\"):
                            break
                    return "\n".join(lines)
            else:
                print("\033[1;4m>>> Response:\033[0m", end="\n")
                print(await chat.ask_question(question))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
