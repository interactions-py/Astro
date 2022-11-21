from datetime import datetime, timedelta, timezone
import interactions
import logging
import src.const
import src.model
from src.const import *
from pymongo.database import *
from time import perf_counter
from asyncio import sleep
from interactions.ext.wait_for import wait_for_component
import asyncio
from typing import Union
from src.exts.gg_protector import GGProtector

log = logging.getLogger("astro.exts.mod")


class Mod(interactions.Extension):
    """An extension dedicated to /mod and other functionalities."""

    def __init__(self, bot, **kwargs):
        self.bot: interactions.Client = bot
        self.db: Database = kwargs.get("db")
        self.actions: Collection = self.db.Moderation
        self._actions = self.actions.find({"id": MOD_ID}).next()["actions"]
        self.gg_protectors: Dict[int, GGProtector] = {}

    async def get_actions(self) -> None:
        self._actions = self.actions.find({"id": MOD_ID}).next()["actions"]

    @interactions.extension_command(scope=METADATA["guild"])
    async def mod(self, ctx: interactions.CommandContext, **kwargs):
        """Handles all moderation aspects."""

        if not self.__check_role(ctx):
            await ctx.send(":x: You are not a moderator.", ephemeral=True)
            return interactions.StopCommand()

    @mod.group()
    async def member(self, *args, **kwargs):
        ...

    @member.subcommand()
    @interactions.option("The user you wish to ban")
    @interactions.option("The reason behind why you want to ban them.")
    async def ban(
        self,
        ctx: interactions.CommandContext,
        member: interactions.Member,
        reason: str = "N/A",
    ):
        """Bans a member from the server and logs into the database."""
        await ctx.defer(ephemeral=True)
        db = self._actions
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.BAN,
            moderator=ctx.author,
            user=member.user,
            reason=reason,
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User banned",
            color=0xED4245,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(name="Reason", value=reason),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)
        await member.ban(guild_id=src.const.METADATA["guild"], reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been banned.", ephemeral=True
        )

    @member.subcommand()
    @interactions.option("The ID of the user you wish to unban.")
    @interactions.option("The reason behind why you want to unban them.")
    async def unban(
        self, ctx: interactions.CommandContext, id: str, reason: str = "N/A"
    ):
        """Unbans a user from the server and logs into the database."""
        await ctx.defer(ephemeral=True)
        db = self._actions
        _id = len(list(db.items())) + 1
        _user: dict = await self.bot._http.get_user(id=id)
        user = interactions.User(**_user)
        action = src.model.Action(
            id=_id,
            type=src.model.ActionType.KICK,
            moderator=ctx.author,
            user=user,
            reason=reason,
        )
        db.update({str(_id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User unbanned",
            color=0x57F287,
            author=interactions.EmbedAuthor(
                name=f"{user.username}#{user.discriminator}",
                icon_url=user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(name="Reason", value=reason),
            ],
        )
        _guild: dict = await self.bot._http.get_guild(src.const.METADATA["guild"])
        guild = interactions.Guild(**_guild, _client=self.bot._http)
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await guild.remove_ban(user_id=id, reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {user.mention} has been unbanned.", ephemeral=True
        )

    @member.subcommand()
    @interactions.option("The user you wish to kick")
    @interactions.option("The reason behind why you want to kick them.")
    async def kick(
        self,
        ctx: interactions.CommandContext,
        member: interactions.Member,
        reason: str = "N/A",
    ):
        """Kicks a member from the server and logs into the database."""
        await ctx.defer(ephemeral=True)
        db = self._actions
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.KICK,
            moderator=ctx.author,
            user=member.user,
            reason=reason,
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User kicked",
            color=0xED4245,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(name="Reason", value=reason),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await member.kick(guild_id=src.const.METADATA["guild"], reason=reason)
        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been kicked.", ephemeral=True
        )

    @member.subcommand()
    @interactions.option("The user you wish to warn")
    @interactions.option("The reason behind why you want to warn them.")
    async def warn(
        self,
        ctx: interactions.CommandContext,
        member: interactions.Member,
        reason: str = "N/A",
    ):
        """Warns a member in the server and logs into the database."""
        await ctx.defer(ephemeral=True)
        db = self._actions
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.WARN,
            moderator=ctx.author,
            user=member.user,
            reason=reason,
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User warned",
            color=0xFEE75C,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(name="Reason", value=reason),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been warned.", ephemeral=True
        )

    @member.subcommand()
    @interactions.option("The user you wish to timeout")
    @interactions.option("The reason behind why you want to timeout them.")
    @interactions.option("How long the user should be timeouted in days.")
    @interactions.option(
        "How long the user should be timeouted in hours.",
    )
    @interactions.option(
        "How long the user should be timeouted in minutes.",
    )
    @interactions.option(
        "How long the user should be timeouted in seconds.",
    )
    async def timeout(
        self,
        ctx: interactions.CommandContext,
        member: interactions.Member,
        reason: str = "N/A",
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """Timeouts a member in the server and logs into the database."""
        if not days and not hours and not minutes and not seconds:
            return await ctx.send(
                ":x: missing any indicator of timeout length!", ephemeral=True
            )
        await ctx.defer(ephemeral=True)
        db = self._actions
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.TIMEOUT,
            moderator=ctx.author,
            user=member.user,
            reason=reason,
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User timed out",
            color=0xFEE75C,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(
                    name="Reason", value="N/A" if reason is None else reason
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        time = datetime.now()
        time += timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        await member.modify(
            guild_id=ctx.guild_id, communication_disabled_until=time.isoformat()
        )
        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been timed out until <t:{round(time.timestamp())}:F> (<t:{round(time.timestamp())}:R>).",
            ephemeral=True,
        )

    @member.subcommand()
    @interactions.option("The user you wish to untimeout")
    @interactions.option("The reason behind why you want to untimeout them.")
    async def untimeout(
        self,
        ctx: interactions.CommandContext,
        member: interactions.Member,
        reason: str = "N/A",
    ):
        """Untimeouts a member in the server and logs into the database."""
        await ctx.defer(ephemeral=True)
        db = self._actions
        id = len(list(db.items())) + 1
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.TIMEOUT,
            moderator=ctx.author,
            user=member.user,
            reason=reason,
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User untimed out",
            color=0xFEE75C,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{ctx.author.mention} ({ctx.author.user.username}#{ctx.author.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(
                    name="Reason", value="N/A" if reason is None else reason
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        if member.communication_disabled_until is None:
            return await ctx.send(
                f":x: {member.mention} is not timed out.", ephemeral=True
            )

        await member.modify(guild_id=ctx.guild_id, communication_disabled_until=None)
        await channel.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been untimed out.", ephemeral=True
        )

    @mod.group()
    async def channel(self, *args, **kwargs):
        ...

    @channel.subcommand()
    @interactions.option("The amount of messages you want to delete")
    @interactions.option("Whether bulk delete should be used, default True")
    @interactions.option("The reason behind why you want purge.")
    @interactions.option(
        "The channel that should be purged",
        channel_types=[interactions.ChannelType.GUILD_TEXT],
    )
    @interactions.autodefer(ephemeral=True)
    async def purge(
        self,
        ctx: interactions.CommandContext,
        amount: int,
        bulk: bool = True,
        reason: str = "N/A",
        channel: interactions.Channel = None,
    ):
        """Purges an amount of message of a channel."""
        if not channel:
            channel = await ctx.get_channel()

        begin = perf_counter()
        await channel.purge(amount=amount, bulk=bulk, reason=reason)
        end = perf_counter()

        if end - begin >= 900:  # more than 15m
            time = datetime.now() + timedelta(seconds=60)
            msg = await channel.send(
                f":heavy_check_mark: {channel.mention} was purged. {ctx.author.mention} \n"
                f"**I will self-destruct in <t:{time.timestamp()}:R>**!"
            )
            await sleep(60)
            await msg.delete()

        else:
            await ctx.send(
                f":heavy_check_mark: {channel.mention} was purged. ", ephemeral=True
            )

    @channel.subcommand()
    @interactions.option("The amount of time to be set as slowmode.")
    @interactions.option("The reason behind why you want to add slow-mode.")
    @interactions.option(
        "The channel that should be slowmoded",
        channel_types=[interactions.ChannelType.GUILD_TEXT],
    )
    @interactions.autodefer(ephemeral=True)
    async def slowmode(
        self,
        ctx: interactions.CommandContext,
        time: int,
        reason: str = "N/A",
        channel: interactions.Channel = None,
    ):
        """Sets the slowmode in a channel."""
        if not channel:
            channel = await ctx.get_channel()

        await channel.modify(rate_limit_per_user=time, reason=reason)
        await ctx.send(
            f":heavy_check_mark: {channel.mention}'s slowmode was set!", ephemeral=True
        )

    @channel.subcommand()
    @interactions.option("The reason of the lock.")
    async def lock(self, ctx: interactions.CommandContext, reason: str = "N/A"):
        """Locks the current channel."""
        await ctx.get_channel()

        overwrites = ctx.channel.permission_overwrites

        for overwrite in overwrites:
            if int(overwrite.id) == int(ctx.guild_id):
                overwrite.deny |= interactions.Permissions.SEND_MESSAGES
                break
        else:
            overwrites.append(
                interactions.Overwrite(
                    id=str(ctx.guild_id),
                    deny=interactions.Permissions.SEND_MESSAGES,
                    type=0,
                )
            )

        await ctx.channel.modify(reason=reason, permission_overwrites=overwrites)

    @channel.subcommand()
    @interactions.option("The reason of the unlock")
    async def unlock(self, ctx: interactions.CommandContext, reason: str = "N/A"):
        await ctx.get_channel()

        overwrites = ctx.channel.permission_overwrites

        for overwrite in overwrites:
            if int(overwrite.id) == int(ctx.guild_id):
                overwrite.deny &= ~interactions.Permissions.SEND_MESSAGES
                overwrite.allow |= interactions.Permissions.SEND_MESSAGES
                break
        else:
            overwrites.append(
                interactions.Overwrite(
                    id=str(ctx.guild_id),
                    allow=interactions.Permissions.SEND_MESSAGES,
                    type=0,
                )
            )

        await ctx.channel.modify(reason=reason, permission_overwrites=overwrites)

    def __check_role(self, ctx: interactions.CommandContext) -> bool:
        """Checks whether an invoker has the Moderator role or not."""
        # TODO: please get rid of me when perms v2 is out. this is so dumb.
        # no bc perm system not good for this
        return bool(
            str(src.const.METADATA["roles"]["Moderator"])
            in [str(role) for role in ctx.author.roles]
        )

    @interactions.extension_listener()
    async def on_message_delete(self, message: interactions.Message):
        embed = interactions.Embed(
            title="Message deleted",
            color=0xED4245,
            author=interactions.EmbedAuthor(
                name=f"{message.author.username}#{message.author.discriminator}",
                icon_url=message.author.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="ID", value=str(message.author.id), inline=True
                ),
                interactions.EmbedField(
                    name="Message",
                    value=message.content
                    if message.content
                    else "**Message could not be retrieved.**",
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["mod-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

    @interactions.extension_listener()
    async def on_message_update(
        self, before: interactions.Message, after: interactions.Message
    ):
        embed = interactions.Embed(
            title="Message updated",
            color=0xED4245,
            author=interactions.EmbedAuthor(
                name=f"{before.author.username}#{before.author.discriminator}",
                icon_url=before.author.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="ID", value=str(before.author.id), inline=True
                ),
                interactions.EmbedField(
                    name="Before:",
                    value=before.content
                    if before.content
                    else "**Message could not be retrieved.**",
                ),
                interactions.EmbedField(
                    name="After:",
                    value=after.content
                    if after.content
                    else "**Message could not be retrieved.**",
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["mod-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

    async def ban_from_member_add(
        self, member: interactions.GuildMember, guild_id: int
    ):
        db = self._actions
        id = len(list(db.items())) + 1
        mod = await interactions.get(
            self.bot,
            interactions.Member,
            object_id=int(self.bot.me.id),
            parent_id=guild_id,
        )
        action = src.model.Action(
            id=id,
            type=src.model.ActionType.BAN,
            moderator=mod,
            user=member.user,
            reason="banned alt of gg cola",
        )
        db.update({str(id): action._json})
        self.actions.find_one_and_update({"id": MOD_ID}, {"$set": {"actions": db}})
        await self.get_actions()
        embed = interactions.Embed(
            title="User banned",
            color=0xED4245,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Moderator",
                    value=f"{mod.mention} ({mod.user.username}#{mod.user.discriminator})",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
                interactions.EmbedField(name="Reason", value="banned alt of gg cola"),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["action-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)
        await member.ban(reason="banned alt of gg cola")
        await channel.send(embeds=embed)

    @staticmethod
    def gg_cola_check(user: interactions.User) -> bool:
        gg_cola_identification_strings: set[str] = {"gg_", "goodgame_", "good_game_"}

        if any(
            user.username.lower().startswith(string)
            for string in gg_cola_identification_strings
        ):
            return True

    async def account_age_check(
        self, member: Union[interactions.Member, interactions.GuildMember]
    ) -> Union[GGProtector, bool]:

        now = datetime.now(timezone.utc)
        min_account_age_before_join: dict = {"days": 2}
        timeout_time: dict = {"days": 1}

        if member.joined_at.replace(tzinfo=timezone.utc) < (member.id.timestamp + timedelta(**min_account_age_before_join)).replace(tzinfo=timezone.utc):
            await member.modify(
                communication_disabled_until=(
                    now + timedelta(**timeout_time)
                ).isoformat()
            )

            await member.send(
                "Hi!\n"
                "We, the interactions.py server, are currently suffering because of a person who is "
                "constantly ban-evading and rejoining our server with alt accounts.\n"
                "Since your account age is less than two days, you have been muted for "
                f"{list(min_account_age_before_join.values())[0]} {list(min_account_age_before_join.keys())[0]}\n"
                "Unfortunately we have been forced to take such extreme measures, since this user leaves us no other"
                "choice.\n\n"
                "The server staff has been "
                "notified of your arrival and will remove your timeout as soon as possible if you are not an "
                "alternative account of that particular person.\n\n"
                "We apologize for any inconvenience\n"
                "The interactions.py-team. "
            )

            gg_prot = GGProtector(self, member)
            self.gg_protectors[int(member.id)] = gg_prot

            return gg_prot

        else:
            return False

    @interactions.extension_listener()
    async def on_guild_member_add(self, member: interactions.GuildMember):

        if self.gg_cola_check(member.user):
            staff = await interactions.get(
                self.bot, interactions.Channel, object_id=820672900583522335
            )

            insta_ban = interactions.Button(
                label="Ban immediately",
                custom_id="bye",
                style=interactions.ButtonStyle.SUCCESS,
            )
            cancel = interactions.Button(
                label="Cancel Ban",
                custom_id="stop",
                style=interactions.ButtonStyle.DANGER,
            )

            time = datetime.now() + timedelta(seconds=60)
            components = [insta_ban, cancel]

            msg = await staff.send(
                "<@&789041109208793139>"
                "\n\n⚠️ Attention⚠️\nI've detected a possible `GG`-guy-alt account:\n"
                f"{member.mention}\n\n"
                f"I will proceed the account automatically in <t:{round(time.timestamp())}:R>"
                "If you don't cancel the ban.\n",
                components=components,
            )

            try:
                data: interactions.ComponentContext = await wait_for_component(
                    self.bot, components=components, timeout=60
                )

                if data.custom_id == "bye":
                    await data.send("<:blobpain:893296401415561246>", ephemeral=True)
                    raise asyncio.TimeoutError()

            except asyncio.TimeoutError:
                insta_ban.disabled = True
                cancel.disabled = True
                await msg.edit(
                    f"{msg.content}\n\nbanned.... <:blobpain:893296401415561246>",
                    components=[insta_ban, cancel],
                )
                await self.ban_from_member_add(member, int(member.guild_id))
                await staff.send("User banned!")

            else:
                insta_ban.disabled = True
                cancel.disabled = True

                await data.defer(edit_origin=True)
                content = data.message.content
                await data.edit(
                    f"{content}\n\nBanning has been cancelled!",
                    components=[insta_ban, cancel],
                )

            return

        elif await self.account_age_check(member):
            staff = await interactions.get(
                self.bot, interactions.Channel, object_id=820672900583522335
            )

            ban_vote_add = interactions.Button(
                label="Add ban vote",
                custom_id="vote_ban_add",
                style=interactions.ButtonStyle.DANGER,
            )
            timeout_remove_vote_add = interactions.Button(
                label="Add timeout removal vote",
                custom_id="add_vote_timeout",
                style=interactions.ButtonStyle.DANGER,
            )

            components = [ban_vote_add, timeout_remove_vote_add]

            msg = await staff.send(
                "<@&789041109208793139>"
                "\n\n⚠️ Attention⚠️\n"
                "I've detected a possible `GG`-guy-alt account by account age:\n"
                f"{member.mention}\n\n",
                components=components,
                embeds=interactions.Embed(
                    title="UserID dumb save hack xd", description=str(member.id)
                ),
            )

        embed = interactions.Embed(
            title="User joined",
            color=0x57F287,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(name="ID", value=str(member.user.id)),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["mod-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)

    async def check_protector(
        self, ctx: interactions.ComponentContext
    ) -> Union[GGProtector, bool]:
        _id = int(ctx.message.embeds[0].description)
        if protector := self.gg_protectors.get(_id):
            return protector
        else:
            await ctx.send("Threat already resolved!", ephemeral=True)
            components = ctx.message.components

            for _components in components:
                for component in _components.components:
                    component.disabled = True

            await ctx.message.edit(components=components)
            return False

    @interactions.extension_component("vote_ban_add")
    async def _ban_add(self, ctx: interactions.ComponentContext):
        if protector := await self.check_protector(ctx):
            if not await protector.increase_ban_votes(ctx.author):
                await ctx.send("already voted, removing your vote", ephemeral=True)
                return await protector.decrease_ban_votes(ctx.author)
            return await ctx.send("vote added!", ephemeral=True)

    @interactions.extension_component("add_vote_timeout")
    async def _timeout_remove_add(self, ctx: interactions.ComponentContext):
        if protector := await self.check_protector(ctx):
            if not await protector.increase_timeout_votes(ctx.author):
                await ctx.send("already voted, removing your vote", ephemeral=True)
                return await protector.decrease_timeout_votes(ctx.author)
            return await ctx.send("vote added!", ephemeral=True)

    @interactions.extension_listener()
    async def on_guild_member_remove(self, member: interactions.GuildMember):
        embed = interactions.Embed(
            title="User left",
            color=0xED4245,
            thumbnail=interactions.EmbedImageStruct(
                url=member.user.avatar_url, height=256, width=256
            )._json,
            author=interactions.EmbedAuthor(
                name=f"{member.user.username}#{member.user.discriminator}",
                icon_url=member.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(name="ID", value=str(member.user.id)),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(member.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(member.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                ),
            ],
        )
        _channel: dict = await self.bot._http.get_channel(
            src.const.METADATA["channels"]["mod-logs"]
        )
        channel = interactions.Channel(**_channel, _client=self.bot._http)

        await channel.send(embeds=embed)


def setup(bot, **kwargs):
    Mod(bot, **kwargs)
