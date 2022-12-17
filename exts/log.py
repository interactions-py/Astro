import asyncio

import naff

from common.const import *


class Log(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.client = bot
        self.mod_log: naff.GuildText = None  # type: ignore

        self.negative_color = naff.Color(0xED4245)
        self.positive_color = naff.Color(0x57F287)

        asyncio.create_task(self.fill_mod_log())

    async def fill_mod_log(self):
        await self.bot.wait_until_ready()
        self.mod_log = self.bot.get_channel(METADATA["channels"]["mod-logs"])  # type: ignore

    def timestamps_for_user(self, user: naff.Member | naff.User):
        return (
            "Joined:"
            f" {user.joined_at.format('R') if isinstance(user, naff.Member) else 'N/A'}\nCreated:"
            f" {user.created_at.format('R')}"
        )

    def generate_base(self, title: str, author: naff.Member | naff.User, color: naff.Color):
        embed = naff.Embed(title=title, color=color)
        embed.set_author(author.tag, author.display_avatar.as_url())
        return embed

    @naff.listen("message_delete")
    async def on_message_delete(self, event: naff.events.MessageDelete):
        embed = self.generate_base("Message deleted", event.message.author, self.negative_color)
        embed.add_field("Author Mention", event.message.author.mention)
        embed.add_field("Message ID", event.message.id)
        embed.add_field(
            "Message",
            event.message.content[:1024]
            if event.message.content
            else "Message could not be retrieved.",
        )

        await self.mod_log.send(embeds=embed)

    @naff.listen("message_update")
    async def on_message_update(self, event: naff.events.MessageUpdate):
        before = event.before
        after = event.after

        if before.content == after.content:
            return

        if not before.content and not after.content:
            return

        embed = self.generate_base("Message updated", after.author, self.negative_color)
        embed.add_field("Author Mention", after.author.mention)
        embed.add_field("Message ID", f"[{after.id}]({after.jump_url})")
        embed.add_field(
            "Before", before.content[:1024] if before.content else "Message could not be retrieved."
        )
        embed.add_field(
            "After", after.content[:1024] if after.content else "Message could not be retrieved."
        )

        await self.mod_log.send(embeds=embed)

    @naff.listen("member_add")
    async def on_member_add(self, event: naff.events.MemberAdd):
        if event.guild_id != METADATA["guild"]:
            return

        member = event.member

        embed = self.generate_base("User joined", member, self.positive_color)
        embed.add_field("User", f"{member.mention} - {member.id}")
        embed.add_field("Timestamps", self.timestamps_for_user(member))

        await self.mod_log.send(embeds=embed)

    @naff.listen("member_remove")
    async def on_member_remove(self, event: naff.events.MemberRemove):
        member = event.member

        embed = self.generate_base("User left", member, self.negative_color)
        embed.add_field("User", f"{member.mention} - {member.id}")
        embed.add_field("Timestamps", self.timestamps_for_user(member))

        await self.mod_log.send(embeds=embed)
