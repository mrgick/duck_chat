import sys

from .api import DuckChat
from .config import ModelType

HELP_MSG = """
\033[1;1m- /help         \033[0mDisplay the help message
\033[1;1m- /singleline   \033[0mEnable singleline mode, validate is done by <enter>
\033[1;1m- /multiline    \033[0mEnable multiline mode, validate is done by EOF <Ctrl+D>
\033[1;1m- /quit         \033[0mQuit"""[1:] # noqa


async def run():
    async with DuckChat(model=ModelType.read_model_from_conf()) as chat:
        INPUT_MODE = "singleline"
        print("Type \033[1;4m/help\033[0m to display the help")
        while True:
            print("\033[1;4m>>> User input:\033[0m", end="\n")

            # get user question
            if INPUT_MODE == "singleline":
                user_input = input().strip()
            else:
                user_input = sys.stdin.read().strip()

            # if user input is command
            if user_input.startswith("/"):
                print("\033[1;4m>>> Command response:\033[0m")
                match user_input[1:]:
                    case "singleline":
                        INPUT_MODE = "singleline"
                        print(
                            "Switched to singleline mode, validate is done by <enter>"
                        )
                    case "multiline":
                        INPUT_MODE = "multiline"
                        print(
                            "Switched to multiline mode, validate is done by EOF <Ctrl+D>"
                        )
                    case "quit":
                        print("Quit")
                        sys.exit(0)
                    case "help":
                        print(HELP_MSG)
                    case _:
                        print("Command doesn't find")
                        print("Type \033[1;4m/help\033[0m to display the help")
                continue

            # empty user input
            if not user_input:
                continue

            print("\033[1;4m>>> Response:\033[0m", end="\n")
            print(await chat.ask_question(user_input))
