import asyncio

import interactions as ipy

from common.const import *


class UserExt(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.client = bot
        self.action_logs: ipy.GuildText = None  # type: ignore
        asyncio.create_task(self.fill_action_logs())

    async def fill_action_logs(self):
        await self.bot.wait_until_ready()
        self.action_logs = self.bot.get_channel(METADATA["channels"]["logs"])  # type: ignore

    @ipy.context_menu("Get User Information", context_type=ipy.CommandType.USER)
    async def get_user_information(self, ctx: ipy.InteractionContext):
        member: ipy.Member | ipy.User = ctx.target  # type: ignore

        roles = list(reversed(sorted(member.roles if isinstance(member, ipy.Member) else [])))
        color_to_use = next(
            (r.color for r in roles if r.color.value),
            member.accent_color or ASTRO_COLOR,
        )

        embed = ipy.Embed(
            title="User Information",
            description=f"This is the retrieved information on {member.mention}.",
            color=color_to_use,
        )
        embed.set_author(
            member.display_name,
            f"https://discord.com/users/{member.id}",
            member.display_avatar.as_url(size=128),
        )
        embed.set_thumbnail(member.display_avatar.as_url())

        embed.add_field("Username", member.tag, inline=True)
        embed.add_field("ID", member.id, inline=True)
        embed.add_field(
            "Timestamps",
            (
                "Joined:"
                f" {member.joined_at.format('R') if isinstance(member, ipy.Member) else 'N/A'}\nCreated:"
                f" {member.created_at.format('R')}"
            ),
            inline=True,
        )
        embed.add_field("Roles", ", ".join(r.mention for r in roles) if roles else "N/A")

        await ctx.send(embed=embed, ephemeral=True)

    @ipy.context_menu("Report User", context_type=ipy.CommandType.USER)
    async def report_user(self, ctx: ipy.ContextMenuContext):
        member: ipy.Member | ipy.User = ctx.target  # type: ignore
        if not isinstance(member, ipy.Member):
            raise ipy.errors.BadArgument("This user has left the server.")

        if member.id == ctx.author.id:
            raise ipy.errors.BadArgument("You cannot report yourself.")

        modal = ipy.Modal(
            ipy.ParagraphText(
                label="Why are you reporting this user?",
                custom_id="report_user_reason",
                min_length=30,
                max_length=1024,
            ),
            title="Report user",
            custom_id=f"astro_report_user_{member.id}",
        )
        await ctx.send_modal(modal)
        await ctx.send(":white_check_mark: Modal sent.", ephemeral=True)

    @ipy.listen("modal_completion")
    async def report_handling(self, event: ipy.events.ModalCompletion):
        ctx = event.ctx

        if ctx.custom_id.startswith("astro_report_user_"):
            member_id = ctx.custom_id.removeprefix("astro_report_user_")
            member = ctx.guild.get_member(int(member_id))  # type: ignore

            if not member:
                await ctx.send(
                    ":x: Could not report user - they likely left the server.",
                    ephemeral=True,
                )
                return

            embed = ipy.Embed(
                title="User Reported",
                color=ipy.MaterialColors.DEEP_ORANGE,
            )
            embed.set_author(member.tag, icon_url=member.display_avatar.as_url(size=128))
            embed.add_field("Reported User", f"<@{member_id}>", inline=True)
            embed.add_field("Reported By", ctx.author.mention, inline=True)
            embed.add_field("Reason", ctx.responses.get("report_user_reason", "N/A"), inline=False)

            await self.action_logs.send(embed=embed)
            await ctx.send(":white_check_mark: Report sent.", ephemeral=True)


def setup(bot):
    UserExt(bot)
