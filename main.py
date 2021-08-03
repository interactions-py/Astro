import logging

import discord
import discord_slash
from discord.ext import commands
from discord_slash.utils import manage_commands

from modules import page
from modules import sphinx_parser
from modules import sqlite_db
from modules.get_settings import get_settings, sanity_check

sanity_check()

bot = commands.Bot(
    command_prefix="/",
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(everyone=False),
    help_command=None,
)
slash = discord_slash.SlashCommand(bot, sync_commands=False)
bot.db = sqlite_db.SQLiteDB("data")

guild_ids = get_settings("servers")

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f"slash.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


@slash.slash(
    name="subscribe", guild_ids=guild_ids, description="Subscribes to new release."
)
async def _subscribe(ctx: discord_slash.SlashContext):
    user = ctx.author
    if [x for x in user.roles if x.id == get_settings("sub_role_id")]:
        return await ctx.send("You are already subscribed!", hidden=True)
    await user.add_roles(ctx.guild.get_role(get_settings("sub_role_id")))
    await ctx.send("Successfully subscribed to new release!", hidden=True)


@slash.slash(
    name="unsubscribe",
    guild_ids=guild_ids,
    description="Unsubscribes from new release.",
)
async def _unsubscribe(ctx: discord_slash.SlashContext):
    user = ctx.author
    if not [x for x in user.roles if x.id == get_settings("sub_role_id")]:
        return await ctx.send("You are already unsubscribed!", hidden=True)
    await user.remove_roles(ctx.guild.get_role(get_settings("sub_role_id")))
    await ctx.send("Successfully unsubscribed to new release!", hidden=True)


@slash.slash(
    name="search",
    guild_ids=guild_ids,
    description="Searches the docs for the given text",
    options=[manage_commands.create_option("text", "Text to search.", 3, True)],
)
async def _docs(ctx: discord_slash.SlashContext, text: str):
    await ctx.defer()
    base_url = "https://discord-py-slash-command.readthedocs.io/en/latest/"
    resp = await sphinx_parser.search_from_sphinx(base_url + "genindex.html", text)
    if not resp:
        return await ctx.send("No result found.")
    base_embed = discord.Embed(
        title="Document Search", color=discord.Color.from_rgb(225, 225, 225)
    )
    base_embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
    count = 1
    embed_list = []
    page_embed = base_embed.copy()
    for_res = resp.copy()
    for x in for_res:
        if count != 1 and count % 5 == 1:
            embed_list.append(page_embed)
            page_embed = base_embed.copy()
        link = base_url + x
        try:
            page_embed.add_field(
                name=str(count), value=f"[`{x.split('#')[1]}`]({link})", inline=False
            )
        except IndexError:
            continue
        resp.remove(x)
        count += 1
    embed_list.append(page_embed)
    if not embed_list:
        return await ctx.send("No result found.")
    await ctx.send(":arrow_down: Look here for results", hidden=True)
    await page.start_page(bot, ctx, embed_list, embed=True)


bot.load_extension("cogs.git")
bot.load_extension("cogs.language")
bot.load_extension("cogs.tags")
bot.load_extension("cogs.buttons")
bot.load_extension("cogs.examples")
bot.run(get_settings("token"))
