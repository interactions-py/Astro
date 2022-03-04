import interactions
import json
import logging
import src.cmds.mod
import src.const
import src.model

log = logging.getLogger("astro.exts.mod")

class Mod(interactions.Extension):
    """An extension dedicated to /mod and other functionalities."""

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(**src.cmds.mod.cmd)
    async def mod(
            self,
            ctx: interactions.CommandContext,
            sub_command_group: str="",
            sub_command: str="",
            user: interactions.User=None,
            reason: str=None,
            id: int=0,
    ):
        log.debug("We've detected /mod, matching...")

        if not self.__check_role(ctx):
            await ctx.send(":x: You are not a moderator.", ephemeral=True)
        else:
            match sub_command_group:
                case "member":
                    match sub_command:
                        case "ban":
                            await self._ban_member(ctx, user, reason)
                        case "unban":
                            await self._unban_member(ctx, id, reason)
                        case "kick":
                            await self._kick_member(ctx, user, reason)
                        case "warn":
                            await self._warn_member(ctx, user, reason)

    async def _ban_member(self, ctx: interactions.CommandContext, member: interactions.Member, reason: str="N/A"):
        """Bans a member from the server and logs into the database."""
        db = json.loads(open("./db/actions.json", "r").read())
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.BAN,
            moderator=ctx.author,
            user=member.user,
            reason=reason
        )
        db.update({str(id): action._json})
        db = open("./db/actions.json", "w").write(json.dumps(db))
        embed = interactions.Embed(
            title="User banned",
            description="This is the information we've been given about the ban.",
            color=0xED4245,
            thumbnail=interactions.EmbedImageStruct(url=member.user.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="User",
                    value=member.mention,
                    inline=True,
                ),
                interactions.EmbedField(name="Moderator", value=ctx.author.mention, inline=True),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                    inline=True,
                ),
                interactions.EmbedField(name="Reason", value=reason)
            ]
        )
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["action-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)
        await member.ban(guild_id=src.const.METADATA["guild"], reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(f":heavy_check_mark: {member.mention} has been banned.", ephemeral=True)

    async def _unban_member(self, ctx: interactions.CommandContext, id: int, reason: str="N/A"):
        """Unbans a user from the server and logs into the database."""
        db = json.loads(open("./db/actions.json", "r").read())
        _id = len(list(db.items())) + 1
        _user: dict = await self.bot._http.get_user(id=id)
        user = interactions.User(**_user)
        action = src.model.Action(
            id=_id,
            type=src.model.ActionType.KICK,
            moderator=ctx.author,
            user=user,
            reason=reason
        )
        db.update({str(_id): action._json})
        db = open("./db/actions.json", "w").write(json.dumps(db))
        embed = interactions.Embed(
            title="User unbanned",
            description="This is the information we've been given about the unban.",
            color=0x57F287,
            thumbnail=interactions.EmbedImageStruct(url=user.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="User",
                    value=user.mention,
                    inline=True,
                ),
                interactions.EmbedField(name="Moderator", value=ctx.author.mention, inline=True),
                interactions.EmbedField(name="Reason", value=reason)
            ]
        )
        _guild: dict = await self.bot._http.get_guild(src.const.METADATA["guild"])
        guild = interactions.Guild(**_guild, _client=self.bot._http)
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["action-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await guild.remove_ban(user_id=id, reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(f":heavy_check_mark: {user.mention} has been unbanned.", ephemeral=True)

    async def _kick_member(self, ctx: interactions.CommandContext, member: interactions.Member, reason: str="N/A"):
        """Bans a member from the server and logs into the database."""
        db = json.loads(open("./db/actions.json", "r").read())
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.KICK,
            moderator=ctx.author,
            user=member.user,
            reason=reason
        )
        db.update({str(id): action._json})
        db = open("./db/actions.json", "w").write(json.dumps(db))
        embed = interactions.Embed(
            title="User kicked",
            description="This is the information we've been given about the kick.",
            color=0xED4245,
            thumbnail=interactions.EmbedImageStruct(url=member.user.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="User",
                    value=member.mention,
                    inline=True,
                ),
                interactions.EmbedField(name="Moderator", value=ctx.author.mention, inline=True),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                    inline=True,
                ),
                interactions.EmbedField(name="Reason", value=reason)
            ]
        )
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["action-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await member.kick(guild_id=src.const.METADATA["guild"], reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(f":heavy_check_mark: {member.mention} has been kicked.", ephemeral=True)

    async def _warn_member(self, ctx: interactions.CommandContext, member: interactions.Member, reason: str="N/A"):
        """Warns a member in the server and logs into the database."""
        ...

    def __check_role(self, ctx: interactions.CommandContext) -> bool:
        """Checks whether an invoker has the Moderator role or not."""
        # TODO: please get rid of me when perms v2 is out. this is so dumb.
        return bool(str(src.const.METADATA["roles"]["Moderator"]) in [str(role) for role in ctx.author.roles])

    @interactions.extension_listener
    async def on_message_delete(self, event: interactions.Message):
        _message: dict = await self.bot._http.get_message(
            channel_id=int(event.channel_id),
            message_id=int(event.id)
        )
        message = interactions.Message(**_message, _client=self.bot._http)
        embed = interactions.Embed(
            title="Message deleted",
            description="This is the information we've been given about the message.",
            color=0xED4245,
            thumbnail=interactions.EmbedImageStruct(url=message.author.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="Username",
                    value=f"{message.author.username}#{message.author.discriminator}",
                    inline=True,
                ),
                interactions.EmbedField(name="ID", value=str(message.author.id), inline=True),
                interactions.EmbedField(name="Message", value=message.content)
            ]
        )
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["mod-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

    @interactions.extension_listener
    async def on_message_update(self, message: interactions.Message):
        ...
        # TODO: get back to this once we work more on aggregating cached data for a before/after.

    @interactions.extension_listener
    async def on_guild_member_add(self, member: interactions.GuildMember):
        embed = interactions.Embed(
            title="User joined",
            description="This is the information we've been given about the user.",
            color=0x57F287,
            thumbnail=interactions.EmbedImageStruct(url=member.user.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="Username",
                    value=f"{member.user.username}#{member.user.discriminator}",
                    inline=True,
                ),
                interactions.EmbedField(name="ID", value=str(member.user.id), inline=True),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.user.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                    inline=True,
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["mod-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

    @interactions.extension_listener
    async def on_guild_member_remove(self, member: interactions.GuildMember):
        embed = interactions.Embed(
            title="User left",
            description="This is the information we've been given about the user.",
            color=0xED4245,
            thumbnail=interactions.EmbedImageStruct(url=member.user.avatar_url, height=256, width=256)._json,
            fields=[
                interactions.EmbedField(
                    name="Username",
                    value=f"{member.user.username}#{member.user.discriminator}",
                    inline=True,
                ),
                interactions.EmbedField(name="ID", value=str(member.user.id), inline=True),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Created: <t:{round(member.user.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                    inline=True,
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(src.const.METADATA["channels"]["mod-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

def setup(bot):
    Mod(bot)