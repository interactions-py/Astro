"""
This bot is very simple, since this should be enough I think.
No cog because I'm lazy and want to keep this minimal.
"""

import json
import logging
import discord
import discord_slash
from discord.ext import commands
from discord_slash.utils import manage_commands
from modules import sqlite_db

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
slash = discord_slash.SlashCommand(bot, override_type=True)
db = sqlite_db.SQLiteDB("data")

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f'slash.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_settings(key: str):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        _json = json.load(f)
    return _json.get(key)


async def init_tags():
    tags = await db.res_sql("""SELECT * FROM tags""")
    for x in tags:
        async def template(ctx):
            cmd_id = ctx.command_id
            resp = await db.res_sql("""SELECT value FROM tags WHERE cmd_id=?""", (cmd_id,))
            content = resp[0]["value"]
            await ctx.send(content=content)
        slash.add_slash_command(template, x["name"], guild_ids=[789032594456576001])


@slash.subcommand(base="tag", name="add")
async def _tag_add(ctx: discord_slash.SlashContext, name: str, response: str):
    is_exist = await db.res_sql("""SELECT * FROM tags WHERE name=?""", (name,))
    if is_exist or name in slash.commands.keys():
        return await ctx.send(content="Uh oh. That name already exists.", complete_hidden=True)
    if len(name) < 3:
        return await ctx.send(content="Name should be at least 3 characters or longer.", complete_hidden=True)
    resp = await manage_commands.add_slash_command(bot.user.id,
                                                   bot.http.token,
                                                   ctx.guild.id if not isinstance(ctx.guild, int) else ctx.guild,
                                                   name,
                                                   f"Custom tag by {ctx.author}.")
    cmd_id = resp["id"]
    await db.exec_sql("""INSERT INTO tags VALUES (?, ?, ?, ?)""",
                      (name, response, ctx.author.id if not isinstance(ctx.author, int) else ctx.author, cmd_id))

    async def template(_ctx):
        _cmd_id = _ctx.command_id
        _resp = await db.res_sql("""SELECT value FROM tags WHERE cmd_id=?""", (_cmd_id,))
        content = _resp[0]["value"]
        await _ctx.send(content=content)

    slash.add_slash_command(template, name, guild_ids=[ctx.guild.id if not isinstance(ctx.guild, int) else ctx.guild])
    await ctx.send(content=f"Successfully added tag `{name}`!", complete_hidden=True)


@slash.subcommand(base="tag", name="remove")
async def _tag_remove(ctx: discord_slash.SlashContext, name: str):
    resp = await db.res_sql("""SELECT cmd_id FROM tags WHERE name=? AND user=?""",
                            (name, ctx.author.id if not isinstance(ctx.author, int) else ctx.author))
    if not resp:
        return await ctx.send(content="Tag not found. Check tag name.", complete_hidden=True)
    await manage_commands.remove_slash_command(bot.user.id,
                                               bot.http.token,
                                               ctx.guild.id if not isinstance(ctx.guild, int) else ctx.guild,
                                               resp[0]["cmd_id"])
    await db.exec_sql("""DELETE FROM tags WHERE cmd_id=?""", (resp[0]["cmd_id"],))
    del slash.commands[name]
    await ctx.send(content=f"Successfully removed tag `{name}`!", complete_hidden=True)


@slash.slash(name="subscribe")
async def _subscribe(ctx: discord_slash.SlashContext):
    user: discord.Member = ctx.author if not isinstance(ctx.author, int) else await ctx.guild.fetch_member(ctx.author)
    if [x for x in user.roles if x.id == 789773555792740353]:
        return await ctx.send(content="You are already subscribed!", complete_hidden=True)
    await user.add_roles(ctx.guild.get_role(789773555792740353))
    await ctx.send(content="Successfully subscribed to new release!", complete_hidden=True)


@slash.slash(name="unsubscribe")
async def _unsubscribe(ctx: discord_slash.SlashContext):
    user: discord.Member = ctx.author if not isinstance(ctx.author, int) else await ctx.guild.fetch_member(ctx.author)
    if not [x for x in user.roles if x.id == 789773555792740353]:
        return await ctx.send(content="You are already unsubscribed!", complete_hidden=True)
    await user.remove_roles(ctx.guild.get_role(789773555792740353))
    await ctx.send(content="Successfully unsubscribed to new release!", complete_hidden=True)


bot.loop.create_task(init_tags())

bot.run(get_settings("token"))
