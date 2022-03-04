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
    __slots__ = ("id", "type", "moderator", "user", "reason")

    id: int
    type: ActionType
    moderator: interactions.Member
    user: interactions.User
    reason: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json.update({"moderator": self.moderator._json, "user": self.user._json})
        del self._json["moderator"]["_client"]
        print(self._json)