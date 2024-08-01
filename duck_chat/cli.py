import readline
import sys
import tomllib
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from .api import DuckChat
from .exceptions import DuckChatException
from .models import ModelType

HELP_MSG = (
    "\033[1;1m- /help         \033[0mDisplay the help message\n"
    "\033[1;1m- /singleline   \033[0mEnable singleline mode, validate is done by <enter>\n"
    "\033[1;1m- /multiline    \033[0mEnable multiline mode, validate is done by EOF <Ctrl+D>\n"
    "\033[1;1m- /quit         \033[0mQuit\n"
    "\033[1;1m- /retry        \033[0mRegenerate answer to № prompt (default /retry 1)"
)

COMMANDS = {"help", "singleline", "multiline", "quit", "retry"}


def completer(text: str, state: int) -> str | None:
    origline = readline.get_line_buffer()
    words = origline.split()
    if not origline.startswith("/"):
        return None
    if len(words) < 2 and words[0][1:] not in COMMANDS:
        options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
        if state < len(options):
            return options[state]
    return None


class CLI:

    def __init__(self) -> None:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)
        self.INPUT_MODE = "singleline"
        self.COUNT = 1
        self.console = Console()

    async def run(self) -> None:
        """Base loop program"""
        model = self.read_model_from_conf()
        print(f"Using \033[1;4m{model.value}\033[0m")
        async with DuckChat(model) as chat:
            print("Type \033[1;4m/help\033[0m to display the help")

            while True:
                print(f"\033[1;4m>>> User input №{self.COUNT}:\033[0m", end="\n")

                user_input = self.get_user_input()

                # user input is command
                if user_input.startswith("/"):
                    await self.command_parsing(user_input.split(), chat)
                    continue

                # empty user input
                if not user_input:
                    print("Bad input")
                    continue

                print(f"\033[1;4m>>> Response №{self.COUNT}:\033[0m", end="\n")
                try:
                    self.answer_print(await chat.ask_question(user_input))
                except DuckChatException as e:
                    print(f"Error occurred: {str(e)}")
                else:
                    self.COUNT += 1

    def get_user_input(self) -> str:
        if self.INPUT_MODE == "singleline":
            try:
                user_input = input()
            except EOFError:
                return ""
        else:
            contents = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                contents.append(line)
            user_input = "".join(contents)
        return user_input.strip()

    def switch_input_mode(self, mode: str) -> None:
        if mode == "singleline":
            self.INPUT_MODE = "singleline"
            print("Switched to singleline mode, validate is done by <enter>")
        else:
            self.INPUT_MODE = "multiline"
            print("Switched to multiline mode, validate is done by EOF <Ctrl+D>")

    async def command_parsing(self, args: list[str], chat: DuckChat) -> None:
        """Recognize command"""
        print("\033[1;4m>>> Command response:\033[0m")
        match args[0][1:]:
            case "singleline":
                self.switch_input_mode("singleline")
            case "multiline":
                self.switch_input_mode("multiline")
            case "quit":
                print("Quit")
                sys.exit(0)
            case "help":
                print(HELP_MSG)
            case "retry":
                if self.COUNT == 1:
                    return
                try:
                    count = int(args[1])
                except Exception:
                    count = len(chat.vqd) - 1
                if count < 0:
                    count = -count
                if count >= len(chat.vqd):
                    count = len(chat.vqd) - 1
                print(f"\033[1;4m>>> REDO Response №{count}:\033[0m", end="\n")
                try:
                    self.answer_print(await chat.reask_question(count))
                except DuckChatException as e:
                    print(f"Error occurred: {str(e)}")
                else:
                    self.COUNT = count + 1
            case _:
                print("Command doesn't find")
                print("Type \033[1;4m/help\033[0m to display the help")

    def answer_print(self, query: str) -> None:
        if "`" in query:  # block of code
            self.console.print(Markdown(query))
        else:
            print(query)

    def read_model_from_conf(self) -> ModelType:
        filepath = Path.home() / ".config" / "hey" / "conf.toml"
        if filepath.exists():
            with open(filepath, "rb") as f:
                conf = tomllib.load(f)
                model_name = conf["model"]
            if model_name in (x.name for x in ModelType):
                if model_name == "GPT3":
                    print("\033[1;1m GPT3 is deprecated! Use GPT4o\033[0m")
                return ModelType[model_name]
        return ModelType.Claude


def safe_entry_point() -> None:
    import asyncio

    asyncio.run(CLI().run())
