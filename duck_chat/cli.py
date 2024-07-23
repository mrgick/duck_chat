import sys
import tomllib
from pathlib import Path

from .api import DuckChat
from .models import ModelType

HELP_MSG = (
    "\033[1;1m- /help         \033[0mDisplay the help message\n"
    "\033[1;1m- /singleline   \033[0mEnable singleline mode, validate is done by <enter>\n"
    "\033[1;1m- /multiline    \033[0mEnable multiline mode, validate is done by EOF <Ctrl+D>\n"
    "\033[1;1m- /quit         \033[0mQuit"
)


class CLI:
    INPUT_MODE = "singleline"
    COUNT = 1

    async def run(self) -> None:
        """Base loop program"""
        async with DuckChat(model=self.read_model_from_conf()) as chat:
            print("Type \033[1;4m/help\033[0m to display the help")

            while True:
                print(f"\033[1;4m>>> User input №{self.COUNT}:\033[0m", end="\n")

                # get user question
                if self.INPUT_MODE == "singleline":
                    user_input = sys.stdin.readline().strip()
                else:
                    user_input = sys.stdin.read().strip()

                # if user input is command
                if user_input.startswith("/"):
                    # TODO: very dirty
                    if "/retry" in user_input:
                        if self.COUNT == 1:
                            continue
                        try:
                            count = int(user_input.split()[1])
                        except Exception:
                            count = len(chat.vqd) - 1
                        if count < 0:
                            count = -count
                        print(f"\033[1;4m>>> Response №{count}:\033[0m", end="\n")
                        print(await chat.reask_question(count))
                        self.COUNT = count + 1
                        continue
                    self.command_parsing(user_input[1:])
                    continue

                # empty user input
                if not user_input:
                    print("Bad input")
                    continue

                print(f"\033[1;4m>>> Response №{self.COUNT}:\033[0m", end="\n")
                print(await chat.ask_question(user_input))
                self.COUNT += 1

    def command_parsing(self, command: str) -> None:
        """Recognize command"""
        print("\033[1;4m>>> Command response:\033[0m")
        match command:
            case "singleline":
                self.INPUT_MODE = "singleline"
                print("Switched to singleline mode, validate is done by <enter>")
            case "multiline":
                self.INPUT_MODE = "multiline"
                print("Switched to multiline mode, validate is done by EOF <Ctrl+D>")
            case "quit":
                print("Quit")
                sys.exit(0)
            case "help":
                print(HELP_MSG)
            case _:
                print("Command doesn't find")
                print("Type \033[1;4m/help\033[0m to display the help")

    def read_model_from_conf(self):
        filepath = Path.home() / ".config" / "hey" / "conf.toml"
        if filepath.exists():
            with open(filepath, "rb") as f:
                conf = tomllib.load(f)
                model_name = conf["model"]
            if ModelType[model_name]:
                return ModelType[model_name]
        return ModelType.Claude
