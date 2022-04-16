import interactions
import enum

class ActionType(enum.IntEnum):
    """An enumerable object representing types of moderation actions."""
    BAN = 1
    UNBAN = 2
    KICK = 3
    WARN = 4

class Action(interactions.DictSerializerMixin):
    """An object representing a moderation action."""
    __slots__ = ("_json", "id", "type", "moderator", "user", "reason")

    _json: dict
    id: int
    type: ActionType
    moderator: interactions.Member
    user: interactions.Member
    reason: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json.update({"moderator": self.moderator._json, "user": self.user._json})
        del self._json["moderator"]["_client"]
        if self._json["user"].get("_client"):
            del self._json["user"]["_client"]

class Tag(interactions.DictSerializerMixin):
    """An object representing a custom-made feed."""
    __slots__ = ("_json", "id", "author", "name", "description")

    _json: dict
    id: int | None
    author: interactions.Snowflake
    name: str
    description: str
    created_at: int
    last_edited_at: int | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.author, interactions.Snowflake):
            self._json.update({"author": self.author._snowflake})
