import enum
import typing
from datetime import datetime

from beanie import Document, Indexed


class ActionType(enum.IntEnum):
    """An enumerable object representing types of moderation actions."""

    BAN = 1
    UNBAN = 2
    KICK = 3
    WARN = 4
    TIMEOUT = 5
    UNTIMEOUT = 6


class Action(Document):
    user: typing.Annotated[str, Indexed(str)]
    type: ActionType
    moderator: str
    created_at: datetime
    reason: typing.Optional[str]


class Tag(Document):
    name: typing.Annotated[str, Indexed(str)]
    author_id: str
    description: str
    created_at: datetime
    last_edited_at: typing.Optional[datetime] = None
