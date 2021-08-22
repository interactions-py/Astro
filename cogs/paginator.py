import discord
from discord.ext import commands
from dinteractions_Paginator import Paginator
from discord_slash import cog_ext
from modules.get_settings import get_settings

guild_ids = get_settings("servers")
example1 = """\
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@slash.slash(name="embeds")
async def embeds(ctx: SlashContext):
    one = discord.Embed(title="1st Embed", description="General Kenobi!", color=discord.Color.red())
    two = discord.Embed(title="2nd Embed", description="General Kenobi!", color=discord.Color.orange())
    three = discord.Embed(title="3rd Embed", description="General Kenobi!", color=discord.Color.gold())
    four = discord.Embed(title="4th Embed", description="General Kenobi!", color=discord.Color.green())
    five = discord.Embed(title="5th Embed", description="General Kenobi!", color=discord.Color.blue())
    pages = [one, two, three, four, five]

    await Paginator(bot=bot, ctx=ctx, pages=pages, content=["1", "2", "3", "4", "5"], timeout=60).run()

bot.run("token")
```
"""
example2 = """\
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@slash.slash(name="command")
    async def command(ctx: SlashContext):
    embed1 = discord.Embed(title="Title")
    embed2 = discord.Embed(title="Another Title")
    embed3 = discord.Embed(title="Yet Another Title")
    pages = [embed1, embed2, embed3]

    await Paginator(bot=bot, ctx=ctx,
        pages=pages, content="Hello there",
        prevLabel="Back", nextLabel="Forward",
        prevEmoji="♥", nextEmoji="♥",
        prevStyle=1, nextStyle=2, 
        indexStyle=3, timeout=10).run()
bot.run("token")
```
"""


class paginator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="paginator",
        description="Multiple page embed paginator example",
        guild_ids=guild_ids,
    )
    async def paginator(self, ctx):
        p1 = discord.Embed(
            title="This is an example embed",
            description="This module allows to have infinitetly long multi-page embeds, more information [here](https://pypi.org/project/dinteractions-Paginator/)",
        )
        p2 = discord.Embed(
            title="It's highly customizable",
            description="It allows you to modify all aspects of the paginator, from the title on the buttons, a persistent message, all the way to a timeout!",
        )
        p3 = discord.Embed(
            title="Easy to implement",
            description="All you need to do is install the library (`pip install dinteractions-Paginator`), import it, and you are ready to rock!",
        )
        p4 = discord.Embed(
            title="Simple Example",
            description="The simplest way of implementing it only requires a list of the embeds to be added as pages!",
        )
        p4.add_field(name="Example", value=f"{example1}")
        p5 = discord.Embed(
            title="Customized Example",
            description="You can change all aspects of the paginator by declaring them when calling the function.",
        )
        p6 = discord.Embed(
            title="In depth example",
            description="This is an example that customizes all the aspects of the paginator, and includes a persistent message!",
        )
        p6.add_field(name="Example", value=f"{example2}")
        pages = [p1, p2, p3, p4, p5, p6]
        await Paginator(
            bot=self.bot, ctx=ctx, pages=pages, content="Paginator example", timeout=60
        ).run()


def setup(bot):
    bot.add_cog(paginator(bot))
