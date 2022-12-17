import asyncio
import importlib
import time
from datetime import datetime, timedelta

import naff

import common.models as models
import common.utils as utils
from common.const import *


async def mod_check_wrapper(ctx: naff.Context):
    return utils.mod_check(ctx)


action_to_str = {
    models.ActionType.BAN: "banned",
    models.ActionType.UNBAN: "unbanned",
    models.ActionType.KICK: "kicked",
    models.ActionType.WARN: "warned",
    models.ActionType.TIMEOUT: "timed out",
    models.ActionType.UNTIMEOUT: "untimed out",
}

action_str_to_color = {
    "banned": naff.Color(0xED4245),
    "unbanned": naff.Color(0x57F287),
    "kicked": naff.Color(0xED4245),
    "warned": naff.Color(0xFEE75C),
    "timed out": naff.Color(0xFEE75C),
    "untimed out": naff.Color(0xFEE75C),
}


class Mod(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.client = bot
        self.action_log: naff.GuildText = None  # type: ignore
        self.add_ext_check(mod_check_wrapper)
        asyncio.create_task(self.fill_action_log())

    async def fill_action_log(self):
        await self.bot.wait_until_ready()
        self.action_log = self.bot.get_channel(METADATA["channels"]["action-logs"])  # type: ignore

    def timestamps_for_user(self, user: naff.Member):
        return (
            "Joined:"
            f" {user.joined_at.format('R') if isinstance(user, naff.Member) else 'N/A'}\nCreated:"
            f" {user.created_at.format('R')}"
        )

    def generate_action_embed(
        self,
        member: naff.Member | naff.User,
        moderator: naff.Member,
        action: str,
        reason: str = "N/A",
    ):
        embed = naff.Embed(
            title="User banned",
            color=action_str_to_color[action],
        )
        embed.set_author(member.tag, member.display_avatar.as_url(size=128))
        embed.add_field("Mention", member.mention)
        embed.add_field("Moderator", moderator.mention)

        if isinstance(member, naff.Member):
            embed.add_field("Timestamps", self.timestamps_for_user(member))

        embed.add_field("Reason", reason)
        return embed

    async def process_action(
        self,
        ctx: naff.InteractionContext,
        member: naff.Member | naff.User,
        action: models.ActionType,
        reason: str = "N/A",
    ):
        await models.Action(
            user=str(member.id),
            type=action,
            moderator=str(ctx.author.id),
            created_at=datetime.now(),
            reason=reason,
        ).insert()

        embed = self.generate_action_embed(member, ctx.author, action_to_str[action], reason)
        await self.action_log.send(embeds=embed)
        await ctx.send(
            f":heavy_check_mark: {member.mention} has been {action_to_str[action]}.", ephemeral=True
        )

    mod = naff.SlashCommand(
        name="mod",
        description="Handles all moderation aspects.",
        default_member_permissions=naff.Permissions.MANAGE_MESSAGES,
    )

    member = mod.group("member", "Actions related to members.")

    @member.subcommand(
        sub_cmd_name="ban",
        sub_cmd_description="Bans a member from the server and logs into the database.",
    )
    async def ban(
        self,
        ctx: naff.InteractionContext,
        member: typing.Annotated[
            naff.Member, naff.slash_user_option("The user you wish to ban.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option("The reason behind why you want to ban them.", required=False),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)

        try:
            await member.ban(reason=reason)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument(f"Could not ban {member.mention}.") from None

        await self.process_action(ctx, member, models.ActionType.BAN, reason)

    @member.subcommand(
        sub_cmd_name="unban",
        sub_cmd_description="Unbans a user from the server and logs into the database.",
    )
    async def unban(
        self,
        ctx: naff.InteractionContext,
        id: typing.Annotated[
            str, naff.slash_str_option("The ID of the user you wish to unban.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option("The reason behind why you want to unban them.", required=False),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)

        try:
            user = await self.bot.fetch_user(id)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument("Invalid ID provided.") from None
        else:
            if not user:
                raise naff.errors.BadArgument("Invalid ID provided.")

        try:
            await ctx.guild.unban(user, reason)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument(f"Could not unban {user.mention}.") from None

        await self.process_action(ctx, user, models.ActionType.UNBAN, reason)

    @member.subcommand(
        sub_cmd_name="kick",
        sub_cmd_description="Kicks a member from the server and logs into the database.",
    )
    async def kick(
        self,
        ctx: naff.InteractionContext,
        member: typing.Annotated[
            naff.Member, naff.slash_user_option("The user you wish to kick.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option("The reason behind why you want to kick them.", required=False),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)

        try:
            await member.kick(reason=reason)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument(f"Could not kick {member.mention}.") from None

        await self.process_action(ctx, member, models.ActionType.KICK, reason)

    @member.subcommand(
        sub_cmd_name="warn",
        sub_cmd_description="Warns a member in the server and logs into the database.",
    )
    async def warn(
        self,
        ctx: naff.InteractionContext,
        member: typing.Annotated[
            naff.Member, naff.slash_user_option("The user you wish to warn.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option("The reason behind why you want to warn them.", required=False),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)

        await ctx.channel.send(f"{member.mention}, you have been warned for reason: {reason}.")
        await self.process_action(ctx, member, models.ActionType.WARN, reason)

    @member.subcommand(
        sub_cmd_name="timeout",
        sub_cmd_description="Timeouts a member in the server and logs into the database.",
    )
    async def timeout(
        self,
        ctx: naff.InteractionContext,
        member: typing.Annotated[
            naff.Member, naff.slash_user_option("The user you wish to timeout.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option(
                "The reason behind why you want to timeout them.", required=False
            ),
        ] = "N/A",
        days: typing.Annotated[
            int,
            naff.slash_int_option("How long the user should be timeouted in days.", required=False),
        ] = 0,
        hours: typing.Annotated[
            int,
            naff.slash_int_option(
                "How long the user should be timeouted in hours.", required=False
            ),
        ] = 0,
        minutes: typing.Annotated[
            int,
            naff.slash_int_option(
                "How long the user should be timeouted in minutes.", required=False
            ),
        ] = 0,
        seconds: typing.Annotated[
            int,
            naff.slash_int_option(
                "How long the user should be timeouted in seconds.", required=False
            ),
        ] = 0,
    ):
        if not days and not hours and not minutes and not seconds:
            raise naff.errors.BadArgument("No timeout length specified.")

        await ctx.defer(ephemeral=True)

        time = naff.Timestamp.utcnow()
        time += timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        try:
            await member.timeout(time, reason)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument(f"Could not timeout {member.mention}.") from None

        await self.process_action(ctx, member, models.ActionType.TIMEOUT, reason)

    @member.subcommand(
        sub_cmd_name="untimeout",
        sub_cmd_description="Untimeouts  a member in the server and logs into the database.",
    )
    async def untimeout(
        self,
        ctx: naff.InteractionContext,
        member: typing.Annotated[
            naff.Member, naff.slash_user_option("The user you wish to untimeout.", required=True)
        ],
        reason: typing.Annotated[
            str,
            naff.slash_str_option(
                "The reason behind why you want to untimeout them.", required=False
            ),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)

        if (
            member.communication_disabled_until is None
            or member.communication_disabled_until < naff.Timestamp.utcnow()
        ):
            raise naff.errors.BadArgument(f"{member.mention} is not timed out.")

        try:
            await member.timeout(None, reason)
        except naff.errors.HTTPException:
            raise naff.errors.BadArgument(f"Could not untimeout {member.mention}.") from None

        await self.process_action(ctx, member, models.ActionType.UNTIMEOUT, reason)

    channel = mod.group("channel", "Actions related to channels.")

    @channel.subcommand(
        sub_cmd_name="purge",
        sub_cmd_description=(
            "Purges an amount of message of a channel. Can only purge messages up to 14 days old."
        ),
    )
    async def purge(
        self,
        ctx: naff.InteractionContext,
        amount: typing.Annotated[
            int, naff.slash_int_option("The amount of messages you want to delete.", required=True)
        ],
        channel: typing.Annotated[
            typing.Optional[naff.GuildText],
            naff.slash_channel_option(
                "The channel that should be purged.", channel_types=[naff.ChannelTypes.GUILD_TEXT]
            ),
        ] = None,
        reason: typing.Annotated[
            str, naff.slash_str_option("The reason behind why you want to purge.", required=False)
        ] = "N/A",
    ):
        purge_channel: naff.GuildText = channel or ctx.channel
        await ctx.send("Purging...", ephemeral=True)

        start = time.perf_counter()
        await purge_channel.purge(deletion_limit=amount, search_limit=amount, reason=reason)
        end = time.perf_counter()

        if end - start >= 900:  # more than 15m
            deletion_time = naff.Timestamp.utcnow() + timedelta(seconds=30)
            await purge_channel.send(
                (
                    f":heavy_check_mark: {purge_channel.mention} was purged,"
                    f" {ctx.author.mention}.\n**I will self-destruct in"
                    f" <t:{deletion_time.timestamp()}:R>**!"
                ),
                delete_after=30,
            )
        else:
            await ctx.send(
                f":heavy_check_mark: {purge_channel.mention} was purged. ", ephemeral=True
            )

    @channel.subcommand(
        sub_cmd_name="slowmode", sub_cmd_description="Sets the slowmode in a channel."
    )
    async def slowmode(
        self,
        ctx: naff.InteractionContext,
        time: typing.Annotated[
            int,
            naff.slash_int_option(
                "The amount of time (in seconds) to be set as slowmode.", required=True
            ),
        ],
        channel: typing.Annotated[
            typing.Optional[naff.GuildText],
            naff.slash_channel_option(
                "The channel that should be slowmoded.",
                channel_types=[naff.ChannelTypes.GUILD_TEXT],
            ),
        ] = None,
        reason: typing.Annotated[
            str,
            naff.slash_str_option(
                "The reason behind why you want to add slowmode.", required=False
            ),
        ] = "N/A",
    ):
        slowmode_channel: naff.GuildText = channel or ctx.channel
        await slowmode_channel.edit(rate_limit_per_user=time, reason=reason)
        await ctx.send(
            f":heavy_check_mark: {slowmode_channel.mention}'s slowmode was set.", ephemeral=True
        )

    @channel.subcommand(sub_cmd_name="lock", sub_cmd_description="Locks a channel.")
    async def lock(
        self,
        ctx: naff.InteractionContext,
        channel: typing.Annotated[
            typing.Optional[naff.GuildText],
            naff.slash_channel_option(
                "The channel that should be locked.", channel_types=[naff.ChannelTypes.GUILD_TEXT]
            ),
        ] = None,
        reason: typing.Annotated[
            str,
            naff.slash_str_option(
                "The reason behind why you want to lock the channel.", required=False
            ),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)
        lock_channel: naff.GuildText = channel or ctx.channel

        overwrites = lock_channel.permission_overwrites
        for overwrite in overwrites:
            if overwrite.id != METADATA["roles"]["Moderator"]:
                overwrite.add_denies(naff.Permissions.SEND_MESSAGES, naff.Permissions.ADD_REACTIONS)

        await lock_channel.edit(permission_overwrites=overwrites, reason=reason)
        await ctx.send(f":heavy_check_mark: {lock_channel.mention} was locked. ", ephemeral=True)

    @channel.subcommand(sub_cmd_name="unlock", sub_cmd_description="Unlocks a channel.")
    async def unlock(
        self,
        ctx: naff.InteractionContext,
        channel: typing.Annotated[
            typing.Optional[naff.GuildText],
            naff.slash_channel_option(
                "The channel that should be unlocked.", channel_types=[naff.ChannelTypes.GUILD_TEXT]
            ),
        ] = None,
        reason: typing.Annotated[
            str,
            naff.slash_str_option(
                "The reason behind why you want to unlock the channel.", required=False
            ),
        ] = "N/A",
    ):
        await ctx.defer(ephemeral=True)
        unlock_channel: naff.GuildText = channel or ctx.channel

        overwrites = unlock_channel.permission_overwrites
        for overwrite in overwrites:
            if overwrite.id != METADATA["roles"]["Moderator"]:
                overwrite.add_allows(naff.Permissions.SEND_MESSAGES, naff.Permissions.ADD_REACTIONS)

        await unlock_channel.edit(permission_overwrites=overwrites, reason=reason)
        await ctx.send(
            f":heavy_check_mark: {unlock_channel.mention} was unlocked. ", ephemeral=True
        )

    @naff.prefixed_command()
    async def sync(self, ctx: naff.PrefixedContext):
        async with ctx.channel.typing:
            await self.bot.synchronise_interactions(
                scopes=[METADATA["guild"]], delete_commands=True
            )
        await ctx.reply("Synchronized commands.")


def setup(bot):
    importlib.reload(utils)
    Mod(bot)
