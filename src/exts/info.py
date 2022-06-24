import interactions
import src.const


class Info(interactions.Extension):
    """An extension dedicated to /info."""

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="info",
        description="Get information about the bot.",
        scope=src.const.METADATA["guild"]
    )
    async def info(self, ctx: interactions.CommandContext):
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
                            f"This project is built with interactions.py `{interactions.base.__version__}`, the no. 1 leading Python interactions library that",
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


def setup(bot):
    Info(bot)
