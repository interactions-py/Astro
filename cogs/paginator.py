import discord
from discord.ext import commands
from dinteractions_Paginator import Paginator as Paginator1
from ButtonPaginator import Paginator as Paginator2
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
    p = Paginator(bot=bot, ctx=ctx, pages=pages, content=["1", "2", "3", "4", "5"], timeout=60)
    data = await p.run()  # wait for the paginator to end for example data
    
bot.run("token")
```
"""

example2 = """\
```py
from ButtonPaginator import Paginator
from discord.ext import commands
from discord_slash import SlashCommand
import discord

bot = commands.Bot("your prefix")
slash = SlashCommand(bot)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
@bot.command()
async def button(ctx):
    embeds = [discord.Embed(title="Page1"), discord.Embed(title="Page3"), discord.Embed(title="Page3")]
    contents = ["Text 1", "Text2", "Text3"]
    e = Paginator(bot=bot,
                  ctx=ctx,
                  header="An example paginator",
                  embeds=embeds,
                  contents=contents,
                  only=ctx.author)
    await e.start()
bot.run("your token")
```
"""


class Paginator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="paginator",
        name="dinteractions-paginator",
        description="Paginator by Jugador and Toricane",
        guild_ids=guild_ids,
    )
    async def paginator1(self, ctx):
        p1 = discord.Embed(
            title="This is an example embed",
            description="This module allows you to have infinitely long multi-page embeds paginated with buttons and a select, more information [here](https://pypi.org/project/dinteractions-Paginator/)",
        )
        p2 = discord.Embed(
            title="It's highly customizable",
            description="It allows you to modify all aspects of the paginator, from the title on the buttons, a changing content, all the way to a timeout!",
        )
        p3 = discord.Embed(
            title="Easy to implement",
            description="All you need to do is install the library (`pip install -U dinteractions-Paginator`), import it, and you are ready to rock!",
        )
        p4 = discord.Embed(
            title="Simple Example",
            description=f"The simplest way of implementing it only requires a list of the embeds to be added as pages!\n\n**Example:**\n{example1}",
        )
        pages = [p1, p2, p3, p4]
        e = Paginator1(
            bot=self.bot,
            ctx=ctx,
            pages=pages,
            content=["One", "Two", "Three", "Four"],
            timeout=60,
        )
        d = await e.run()
        s = ""
        for user in d.successfulUsers:
            s += f"{user.mention}" + (", " if len(d.successfulUsers) > 1 else "")
        await ctx.send(
            f"""
The paginator returns some useful optional data!
{s} used this paginator!
The paginator ran for {d.timeTaken} seconds!
This was the last embed of the paginator:
""",
            embed=d.lastEmbed,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @cog_ext.cog_subcommand(
        base="paginator",
        name="dpy-slash-button-paginator",
        description="Paginator by Catalyst4",
        guild_ids=guild_ids,
    )
    async def paginator2(self, ctx):
        p1 = discord.Embed(
            title="This is an example embed",
            description="This module allows you to have infinitely long multi-page embeds with buttons, more information [here](https://pypi.org/project/dpy-slash-button-paginator/)",
        )
        p2 = discord.Embed(
            title="It's highly customizable",
            description="It allows you to modify all aspects of the paginator, from the title on the buttons, a changing content, all the way to a timeout!",
        )
        p3 = discord.Embed(
            title="Easy to implement",
            description="All you need to do is install the library (`pip install --upgrade dpy-slash-button-paginator`), import it, and you are ready to rock!",
        )
        p4 = discord.Embed(
            title="Simple Example",
            description=f"The simplest way of implementing it only requires a list of the embeds to be added as pages!\n\n**Example:**\n{example2}",
        )
        pages = [p1, p2, p3, p4]
        e = Paginator2(
            bot=self.bot,
            ctx=ctx,
            embeds=pages,
            contents=["One", "Two", "Three", "Four"],
            timeout=60,
            disable_after_timeout=True,
        )
        await e.start()


def setup(bot):
    bot.add_cog(Paginator(bot))
