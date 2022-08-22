import interactions
from src.const import *
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mod import Mod


class GGProtector:
    def __init__(
        self,
        mod: Mod,
        member: interactions.Member,
        guild_id: int = METADATA["guild"],
        min_votes: int = 2,
    ):
        self.ban_votes: int = 0
        self.timeout_votes = 0
        self.member = member
        self.guild_id: int = guild_id
        self.min_ban_votes = min_votes
        self.min_timeout_votes = min_votes
        self.ban_voted: list = []
        self.timeout_voted: list = []
        self.cleared: bool = False
        self.mod = mod

    def __bool__(self):
        return True

    async def increase_ban_votes(self, member: interactions.Member) -> bool:
        if int(member.id) in self.ban_voted:
            return False

        if int(member.id) in self.timeout_voted:
            self.timeout_voted.pop(int(member.id))
            self.timeout_votes -= 1

        self.ban_voted.append(int(member.id))
        self.ban_votes += 1

        await self.check_ban()
        return True

    async def check_ban(self):
        if self.ban_votes >= self.min_ban_votes and not self.cleared:
            await self.member.ban(int(self.guild_id), reason="GG_COLA")
            self.clear()

    async def increase_timeout_votes(self, member: interactions.Member) -> bool:
        if int(member.id) in self.timeout_voted:
            return False

        if int(member.id) in self.ban_voted:
            self.ban_voted.pop(int(member.id))
            self.ban_votes -= 1

        self.timeout_voted.append(int(member.id))
        self.timeout_votes += 1

        await self.check_timeout()
        return True

    async def check_timeout(self):
        if self.timeout_votes >= self.timeout_votes and not self.cleared:
            time = datetime.utcnow()
            await self.member.modify(
                guild_id=self.guild_id, communication_disabled_until=time.isoformat()
            )
            await self.member.send("Your timeout was removed!")
            self.clear()

    async def decrease_timeout_votes(self, member: interactions.Member) -> bool:
        if int(member.id) not in self.timeout_voted:
            return False

        self.timeout_voted.pop(int(member.id))
        self.timeout_votes -= 1

        return True

    async def decrease_ban_votes(self, member: interactions.Member) -> bool:
        if int(member.id) not in self.ban_voted:
            return False

        self.ban_voted.pop(int(member.id))
        self.ban_votes += 1

        return True

    def clear(self):
        self.cleared = True
        del self.mod.gg_protectors[int(self.member.id)]
