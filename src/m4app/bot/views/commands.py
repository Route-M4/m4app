from dataclasses import dataclass

from aiogram.types import BotCommand


@dataclass
class CommandsGroup:
    name: str
    commands: list[BotCommand]

    def __str__(self) -> str:
        return f"{self.name}\n" + "\n".join(
            f"/{x.command} - {x.description}" for x in self.commands
        )


ABOUT_COMMAND = BotCommand(command="about", description="About bot")
CANCEL_COMMAND = BotCommand(command="cancel", description="Cancel command")
HELP_COMMAND = BotCommand(command="help", description="Help command")
START_COMMAND = BotCommand(command="start", description="Start command")

HELP_BASE = CommandsGroup(
    "Basic commands:",
    [
        ABOUT_COMMAND,
        CANCEL_COMMAND,
        HELP_COMMAND,
        START_COMMAND,
    ],
)

HELP_INFO = CommandsGroup("Other commands:", [])

HELP_USER = "\n\n".join(
    map(
        str,
        (HELP_BASE, HELP_INFO),
    ),
)
