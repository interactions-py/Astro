import naff

from common.const import ASTRO_COLOR


class Info(naff.Extension):
    """An extension dedicated to /info."""

    def __init__(self, bot, **kwargs):
        self.bot = bot

    @naff.slash_command(
        "info",
        description="Get information about the bot.",
    )
    async def info(self, ctx: naff.InteractionContext):
        embed = naff.Embed(
            title="Info",
            color=ASTRO_COLOR,
        )
        embed.add_field(
            "What is this for?",
            (
                "Astro is the main bot powering moderation and other utilities in the"
                " interactions.py support server. The goal of Astro is to make searching simple,"
                " and automate our moderation process. Whether that's creating tags with"
                " autocompleted suggestions, code examples, or interactive tutorials: Astro has you"
                " covered. Interactions should be simple to understand, and coding them is no"
                " different."
            ),
        )
        embed.add_field(
            "What does this bot run on?",
            (
                "This project is built with interactions.py, the no. 1 leading Python interactions"
                " library that empowers bots with the ability to implement slash commands and"
                " components with ease. The codebase of this bot reflects how simple, modular and"
                " scalable the library is---staying true to the motto of what it does."
            ),
        )
        embed.add_field(
            "How can I contribute to this bot?",
            (
                "Please check out the official GitHub repository which holds the source code of"
                " this bot here: https://github.com/interactions-py/Astro"
            ),
        )
        embed.set_footer("This bot is maintained by the interactions.py ext team.")
        await ctx.send(embeds=embed)


def setup(bot):
    Info(bot)
