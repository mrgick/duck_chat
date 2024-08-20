from rich.console import Console
from rich.markdown import Markdown

from ..api import DuckChat
from ..exceptions import DuckChatException
from ..models import ModelType
from .commands import Commands
from .config import Settings


class CLI:
    def __init__(self) -> None:
        self.console = Console()
        self.settings = Settings.get_settings()
        self.commands = Commands()

    async def run(self) -> None:
        """Base loop program"""
        model = ModelType[self.settings.MODEL]
        print(f"Using \033[1;4m{model.value}\033[0m")
        async with DuckChat(model) as chat:
            print("Type \033[1;4m/help\033[0m to display the help")
            while True:
                count = len(chat.vqd) or 1
                print(f"\033[1;4m>>> User input №{count}:\033[0m", end="\n")

                user_input = self.get_user_input()

                # user input is command
                if user_input.startswith("/"):
                    await self.commands.command_parsing(
                        args=user_input.split(), chat=chat, settings=self.settings, print_func=self.answer_print
                    )
                    continue

                # empty user input
                if not user_input:
                    print("Bad input")
                    continue

                print(f"\033[1;4m>>> Response №{count}:\033[0m", end="\n")
                try:
                    if self.settings.STREAM_MODE:
                        async for message in chat.ask_question_stream(user_input):
                            print(message, flush=True, end="")
                        print()
                    else:
                        self.answer_print(await chat.ask_question(user_input))
                except DuckChatException as e:
                    print(f"Error occurred: {str(e)}")

    def get_user_input(self) -> str:
        if self.settings.INPUT_MODE == "singleline":
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

    def answer_print(self, query: str) -> None:
        if "`" in query:  # block of code
            self.console.print(Markdown(query))
        else:
            print(query)
