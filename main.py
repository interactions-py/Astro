import interactions
import dotenv
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = dotenv.get_key(".env", "token")
bot = interactions.Client(TOKEN, disable_sync=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name}.")


@bot.user_command(name="Get user information")
async def get_user_info(ctx: interactions.CommandContext):
    embed = interactions.Embed(
        title="User Information",
        description="This is the retrieved information on the user.",
        author=interactions.EmbedAuthor(
            name=f"<@{ctx.target.user.id}>",
            url=f"discord://-/users/{ctx.target.user.id}",
            icon_url=f"https://cdn.discordapp.com/avatars/{ctx.target.user.id}/{ctx.target.avatar}.png",
        ),
        fields=[
            interactions.EmbedField(
                name="Username",
                value=f"{ctx.target.user.username}#{ctx.target.user.discriminator}",
                inline=True,
            ),
            interactions.EmbedField(name="ID", value=ctx.target.user.id, inline=True),
            interactions.EmbedField(
                name="Timestamps",
                value="\n".join(
                    [
                        f"Joined: <t:{ctx.target.joined_at.utcnow()}:R>.",
                        f"Created: <t:{ctx.target.id.timestamp.utcnow()}:R>.",
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
            interactions.EmbedField(name=""),
        ],
    )
    await ctx.send(embeds=embed, ephemeral=True)


@bot.command(name="info", description="Get information about the bot.")
async def info(ctx: interactions.CommandContext):
    embed = interactions.Embed(
        title="Info",
        footer=interactions.EmbedFooter(
            text="This bot is maintained by the interactions.py ext team."
        ),
        fields=[
            interactions.EmbedField(
                name="What is this for?",
                value="".join(
                    [
                        "Astro is the main bot powering moderation and other utilities in the interactions.py support server.",
                        " The goal of Astro is to make searching simple, and automate our moderation process. Whether that's creating tags with",
                        " autocompleted suggestions, code examples, or interactive tutorials: Astro has you covered. Interactions should be simple to understand,",
                        " and coding them is no different.",
                    ]
                ),
            ),
            interactions.EmbedField(
                name="What does this bot run on?",
                value="".join(
                    [
                        "This project is built with interactions.py `4.0.2`, the no. 1 leading Python interactions library that",
                        " empowers bots with the ability to implement slash commands and components with ease. The codebase of this bot reflects how simple,",
                        " modular and scalable the library is---staying true to the motto of what it does.",
                    ]
                ),
            ),
            interactions.EmbedField(
                name="How can I contribute to this bot?",
                value="Please check out the official GitHub repository which holds the source code of this bot here: https://github.com/interactions-py/Astro",
            ),
        ],
    )
    await ctx.send(embeds=embed)


bot.start()
