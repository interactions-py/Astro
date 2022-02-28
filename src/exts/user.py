import interactions

class User(interactions.Extension):
    """An extension dedicated to user context menus."""

    def __init__(self, bot):
        self.bot = bot
        self.reported_user = None

    @interactions.extension_user_command(name="Get user information")
    async def get_user_info(self, ctx: interactions.CommandContext):
        embed = interactions.Embed(
            title="User Information",
            description="This is the retrieved information on the user.",
            thumbnail=interactions.EmbedImageStruct(url=ctx.target.user.avatar_url, height=256, width=256)._json,
            author=interactions.EmbedAuthor(
                name=f"{ctx.target.user.username}",
                url=f"https://discord.com/users/{ctx.target.user.id}",
                icon_url=ctx.target.user.avatar_url,
            ),
            fields=[
                interactions.EmbedField(
                    name="Username",
                    value=f"{ctx.target.user.username}#{ctx.target.user.discriminator}",
                    inline=True,
                ),
                interactions.EmbedField(name="ID", value=str(ctx.target.user.id), inline=True),
                interactions.EmbedField(
                    name="Timestamps",
                    value="\n".join(
                        [
                            f"Joined: <t:{round(ctx.target.joined_at.timestamp())}:R>.",
                            f"Created: <t:{round(ctx.target.id.timestamp.timestamp())}:R>.",
                        ]
                    ),
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Roles",
                    value=", ".join([f"`{role}`" for role in ctx.target.roles])
                    if isinstance(ctx.target, interactions.Member)
                    else "N/A",
                ),
            ],
        )
        await ctx.send(embeds=embed, ephemeral=True)

    @interactions.extension_user_command(name="Report user")
    async def report_user(self, ctx: interactions.CommandContext):
        modal = interactions.Modal(
            title="Report user",
            custom="report_user",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    label="Why are you reporting this user?",
                    custom_id="report_user_reason",
                    min_length=30,
                ),
            ],
        )
        await ctx.popup(modal)
        self.reported_user = ctx.target

    @interactions.extension_modal("report_user")
    async def __report_user(self, ctx: interactions.CommandContext, reason: str):
        _channel: dict = await self.bot._http.get_channel(789041087149899796)
        channel = interactions.Channel(**_channel, _client=self.bot._http)
        await channel.send(f"{ctx.author.mention} reported {self.reported_user.mention} for:\n```\n{reason}\n```")
        await ctx.send(":heavy_check_mark: User reported.", ephemeral=True)

def setup(bot):
    User(bot)