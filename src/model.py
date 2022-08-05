import interactions
import enum

from interactions.api.models.attrs_utils import define, field


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
        converter=interactions.Member, default=None, add_client=True
    )
    user: interactions.Member = field(
        converter=interactions.Member, default=None, add_client=True
    )
    reason: str | None = field(default=None)

    def __attrs_post_init__(self):
        self._json.update({"moderator": self.moderator._json, "user": self.user._json})
        del self._json["moderator"]["_client"]
        if self._json["user"].get("_client"):
            del self._json["user"]["_client"]


@define()
class Tag(interactions.DictSerializerMixin):
    """An object representing a custom-made feed."""

    id: int | None = field(default=None)
    author: interactions.Snowflake = field(converter=interactions.Snowflake)
    name: str = field()
    description: str = field()
    created_at: int = field()
    last_edited_at: int | None = field(default=None)

    def __attrs_post_init__(self):
        if isinstance(self.author, interactions.Snowflake):
            self._json.update({"author": self.author._snowflake})
