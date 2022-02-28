import interactions

class Mod(interactions.Extension):
    """An extension dedicated to /mod and other functionalities."""

    def __init__(self, bot):
        self.bot = bot

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
        _channel: dict = await self.bot._http.get_channel(METADATA["channels"]["mod-logs"])
        channel = interactions.Channel(**_channel, _client=self.bot._http)
        await channel.send(embeds=embed)

def setup(bot):
    Mod(bot)