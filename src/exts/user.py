import interactions

class User(interactions.Extension):
    """An extension dedicated to user context menus."""

    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    User(bot)