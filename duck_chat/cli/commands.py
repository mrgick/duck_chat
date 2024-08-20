import readline
import sys
from typing import Any, Callable

from ..api import DuckChat
from ..exceptions import DuckChatException
from .config import Settings


class Commands:
    def __init__(self) -> None:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        self.COMMANDS: dict[str, Callable[..., Any]] = {
            "help": self.help,
            "singleline": self.singleline,
            "multiline": self.multiline,
            "quit": self.quit,
            "retry": self.retry,
            "stream_on": self.stream_on,
            "stream_off": self.stream_off,
        }

    def completer(self, text: str, state: int) -> str | None:
        origline = readline.get_line_buffer()
        words = origline.split()
        if not origline.startswith("/"):
            return None
        if len(words) < 2 and words[0][1:] not in self.COMMANDS:
            options = [cmd for cmd in self.COMMANDS if cmd.startswith(text)]
            if state < len(options):
                return options[state]
        return None

    async def command_parsing(
        self, args: list[str], chat: DuckChat, settings: Settings, print_func: Callable[[str], None]
    ) -> None:
        """Recognize command"""
        command = args[0][1:]
        print("\033[1;4m>>> Command response:\033[0m")
        if command not in self.COMMANDS:
            print("Command doesn't find")
            print("Type \033[1;4m/help\033[0m to display the help")
            return
        command_func = self.COMMANDS[command]
        await command_func(*args[1:], chat=chat, settings=settings, print_func=print_func)

    async def singleline(self, settings: Settings, *args: Any, **kwargs: Any) -> None:
        """Enable singleline mode, validate is done by <enter>"""
        settings.INPUT_MODE = "singleline"
        print("Switched to singleline mode, validate is done by <enter>")

    async def multiline(self, settings: Settings, *args: Any, **kwargs: Any) -> None:
        """Enable multiline mode, validate is done by EOF <Ctrl+D>"""
        settings.INPUT_MODE = "multiline"
        print("Switched to multiline mode, validate is done by EOF <Ctrl+D>")

    async def stream_on(self, settings: Settings, *args: Any, **kwargs: Any) -> None:
        """Enable stream mode"""
        settings.STREAM_MODE = True
        print("Switched to stream mode")

    async def stream_off(self, settings: Settings, *args: Any, **kwargs: Any) -> None:
        """Disable stream mode"""
        settings.STREAM_MODE = False
        print("Switched to non stream mode")

    async def quit(self, *args: Any, **kwargs: Any) -> None:
        """Quit"""
        print("Quit")
        sys.exit(0)

    async def help(self, *args: Any, **kwargs: Any) -> None:
        """Display the help message"""
        print(
            "\033[1;1m- /help         \033[0mDisplay the help message\n"
            "\033[1;1m- /singleline   \033[0mEnable singleline mode, validate is done by <enter>\n"
            "\033[1;1m- /multiline    \033[0mEnable multiline mode, validate is done by EOF <Ctrl+D>\n"
            "\033[1;1m- /stream_on   \033[0mEnable stream mode\n"
            "\033[1;1m- /stream_off    \033[0mDisable stream mode\n"
            "\033[1;1m- /quit         \033[0mQuit\n"
            "\033[1;1m- /retry        \033[0mRegenerate answer to № prompt (default /retry 1)"
        )

    async def retry(
        self, *args: Any, chat: DuckChat, settings: Settings, print_func: Callable[[str], None], **kwargs: Any
    ) -> None:
        try:
            count = int(args[0])
        except Exception:
            count = len(chat.vqd) - 1
        if count >= len(chat.vqd):
            count = len(chat.vqd) - 1
        if count < 0:
            count = -count
        print(f"\033[1;4m>>> REDO Response №{count}:\033[0m", end="\n")
        try:
            if settings.STREAM_MODE:
                async for message in chat.reask_question_stream(count):
                    print(message, flush=True, end="")
                print()
            else:
                print_func(await chat.reask_question(count))
        except DuckChatException as e:
            print(f"Error occurred: {str(e)}")
