import enum
import typing
from datetime import datetime

import interactions
from beanie import Document, Indexed
from interactions.utils.attrs_utils import define, field


class ActionType(enum.IntEnum):
    """An enumerable object representing types of moderation actions."""

    BAN = 1
    UNBAN = 2
    KICK = 3
    WARN = 4
    TIMEOUT = 5


@define()
class Action(interactions.DictSerializerMixin):
    """An object representing a moderation action."""

    id: int = field()
    type: ActionType = field(converter=ActionType)
    moderator: interactions.Member = field(
        converter=interactions.Member, default=None, add_client=False
    )
    user: interactions.User = field(converter=interactions.User, default=None, add_client=False)
    reason: str | None = field(default=None)

    def __attrs_post_init__(self):
        if self._json["moderator"].get("_client"):
            del self._json["moderator"]["_client"]
        if self._json["moderator"].get("user").get("_client"):
            del self._json["moderator"]["user"]["_client"]
        if self._json["user"].get("_client"):
            del self._json["user"]["_client"]
        del self.moderator._client
        del self.moderator.user._client
        del self.user._client
        self._json.update({"moderator": self.moderator._json, "user": self.user._json})


class Tag(Document):
    name: Indexed(str)
    author_id: str
    description: str
    created_at: datetime
    last_edited_at: typing.Optional[datetime] = None
