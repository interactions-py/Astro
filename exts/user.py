import naff

from common.const import *


class UserExt(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.client = bot
        self.action_logs: naff.GuildText = None  # type: ignore

    async def fill_action_logs(self):
        await self.bot.wait_until_ready()
        self.action_logs = self.bot.get_channel(METADATA["channels"]["action-logs"])  # type: ignore

    @naff.context_menu("Get User Information", naff.CommandTypes.USER)  # type: ignore
    async def get_user_information(self, ctx: naff.InteractionContext):
        member: naff.Member | naff.User = ctx.target  # type: ignore

        roles = reversed(sorted(member.roles if isinstance(member, naff.Member) else []))
        color_to_use = next(
            (r.color for r in roles if r.color.value), member.accent_color or ASTRO_COLOR
        )

        embed = naff.Embed(
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
            "Joined:"
            f" {member.joined_at.format('R') if isinstance(member, naff.Member) else 'N/A'}\nCreated:"
            f" {member.created_at.format('R')}",
            inline=True,
        )
        embed.add_field("Roles", ", ".join(r.mention for r in roles) if roles else "N/A")

        await ctx.send(embed=embed, ephemeral=True)

    @naff.context_menu("Report User", naff.CommandTypes.USER)  # type: ignore
    async def report_user(self, ctx: naff.InteractionContext):
        member: naff.Member | naff.User = ctx.target  # type: ignore
        if not isinstance(member, naff.Member):
            raise naff.errors.BadArgument(":x: This user has left the server.")

        modal = naff.Modal(
            "Report user",
            [
                naff.ParagraphText(
                    "Why are you reporting this user?",
                    "report_user_reason",
                    min_length=30,
                    max_length=1024,
                )
            ],
            custom_id=f"astro_report_user_{member.id}",
        )
        await ctx.send_modal(modal)
        await ctx.send("Modal sent.", ephemeral=True)

    @naff.listen("modal_completion")
    async def report_handling(self, event: naff.events.ModalCompletion):
        ctx = event.ctx

        if ctx.custom_id.startswith("astro_report_user_"):
            member_id = ctx.custom_id.removeprefix("astro_report_user_")
            member = ctx.guild.get_member(int(member_id))  # type: ignore

            if not member:
                await ctx.send(
                    ":x: Could not report user - they likely left the server.", ephemeral=True
                )
                return

            embed = naff.Embed(
                title="User Reported",
                color=naff.MaterialColors.DEEP_ORANGE,
            )
            embed.set_author(member.tag, member.display_avatar.as_url(size=128))
            embed.add_field("Reported User", f"<@{member_id}>", inline=True)
            embed.add_field("Reported By", ctx.author.mention, inline=True)
            embed.add_field("Reason", ctx.responses["report_user_reason"], inline=False)

            await self.action_logs.send(embed=embed)
            await ctx.send(":heavy_check_mark: Report sent.", ephemeral=True)


def setup(bot):
    UserExt(bot)
