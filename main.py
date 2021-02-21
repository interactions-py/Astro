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
from modules import sphinx_parser
from modules import page

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all(), allowed_mentions=discord.AllowedMentions(everyone=False))
slash = discord_slash.SlashCommand(bot, override_type=True)
db = sqlite_db.SQLiteDB("data")
guild_ids = [789032594456576001]

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f'slash.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_settings(key: str):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        _json = json.load(f)
    return _json.get(key)


tag_opt = manage_commands.create_option("reply_to",
                                        "Message ID to reply.",
                                        3,
                                        False)


async def template(ctx, msg_id=None):
    await ctx.send(5)
    resp = await db.res_sql("""SELECT value FROM tags WHERE cmd_id=?""", (ctx.command_id,))
    content = resp[0]["value"]
    if msg_id:
        try:
            msg: discord.Message = await ctx.channel.fetch_message(int(msg_id))
            return await msg.reply(content)
        except (discord.Forbidden, discord.HTTPException, discord.NotFound, TypeError, ValueError):
            await ctx.send(content="Couldn't find message to reply. Normally sending tag.", hidden=True)
    await ctx.send(content=content)


async def init_tags():
    await bot.wait_until_ready()
    tags = await db.res_sql("""SELECT * FROM tags""")
    for x in tags:
        owner = bot.get_user(int(x["user"]))
        owner = str(owner) if owner else "unknown user"
        #slash.add_slash_command(template, x["name"], guild_ids=guild_ids, options=[tag_opt], description=f"Custom tag by {owner}.")
    '''
    await slash.register_all_commands()
    cmds = await manage_commands.get_all_commands(bot.user.id, bot.http.token, 789032594456576001)
    for x in cmds:
        cmd_id = x["id"]
        cmd_name = x["name"]
        if cmd_name in ["tag", "subscribe", "unsubscribe"]:
            continue
        await db.exec_sql("""UPDATE tags SET cmd_id=? WHERE name=?""", (cmd_id, cmd_name))
    '''


add_opt = [
            {
                "name": "name",
                "description": "Name of the tag.",
                "type": 3,
                "required": True
            },
            {
                "name": "response",
                "description": "Response of the tag.",
                "type": 3,
                "required": True
            }
        ]

rm_opt = [
            {
                "name": "name",
                "description": "Name of the tag.",
                "type": 3,
                "required": True
            }
        ]


@slash.subcommand(base="tag", name="add", guild_ids=guild_ids,
                  description="Adds a new tag.", options=add_opt)
async def _tag_add(ctx: discord_slash.SlashContext, name: str, response: str):
    is_exist = await db.res_sql("""SELECT * FROM tags WHERE name=?""", (name,))
    if is_exist or name in slash.commands.keys():
        return await ctx.send(content="Uh oh. That name already exists.", hidden=True)
    if len(name) < 3:
        return await ctx.send(content="Name should be at least 3 characters or longer.", hidden=True)
    resp = await manage_commands.add_slash_command(bot.user.id,
                                                   bot.http.token,
                                                   ctx.guild_id,
                                                   name,
                                                   f"Custom tag by {ctx.author}.",
                                                   options=[tag_opt])
    cmd_id = resp["id"]
    await db.exec_sql("""INSERT INTO tags VALUES (?, ?, ?, ?)""",
                      (name, response, ctx.author_id, cmd_id))

    slash.add_slash_command(template, name, guild_ids=[ctx.guild_id], options=[tag_opt])
    await ctx.send(content=f"Successfully added tag `{name}`!", hidden=True)


@slash.subcommand(base="tag", name="remove", guild_ids=guild_ids,
                  description="Removes existing tag.", options=rm_opt)
async def _tag_remove(ctx: discord_slash.SlashContext, name: str):
    resp = await db.res_sql("""SELECT cmd_id FROM tags WHERE name=? AND user=?""",
                            (name, ctx.author_id))
    if ctx.author_id == 288302173912170497:
        resp = await db.res_sql("""SELECT cmd_id FROM tags WHERE name=?""", (name,))
    if not resp:
        return await ctx.send(content="Tag not found. Check tag name.", hidden=True)
    await manage_commands.remove_slash_command(bot.user.id,
                                               bot.http.token,
                                               ctx.guild_id,
                                               resp[0]["cmd_id"])
    await db.exec_sql("""DELETE FROM tags WHERE cmd_id=?""", (resp[0]["cmd_id"],))
    del slash.commands[name]
    await ctx.send(content=f"Successfully removed tag `{name}`!", hidden=True)


@slash.slash(name="subscribe", guild_ids=guild_ids, description="Subscribes to new release.")
async def _subscribe(ctx: discord_slash.SlashContext):
    user = ctx.author
    if [x for x in user.roles if x.id == 789773555792740353]:
        return await ctx.send(content="You are already subscribed!", hidden=True)
    await user.add_roles(ctx.guild.get_role(789773555792740353))
    await ctx.send(content="Successfully subscribed to new release!", hidden=True)


@slash.slash(name="unsubscribe", guild_ids=guild_ids, description="Unsubscribes to new release.")
async def _unsubscribe(ctx: discord_slash.SlashContext):
    user = ctx.author
    if not [x for x in user.roles if x.id == 789773555792740353]:
        return await ctx.send(content="You are already unsubscribed!", hidden=True)
    await user.remove_roles(ctx.guild.get_role(789773555792740353))
    await ctx.send(content="Successfully unsubscribed to new release!", hidden=True)


@slash.slash(name="search", guild_ids=guild_ids, description="Searches given text to the document.",
             options=[manage_commands.create_option("text", "Text to search.", 3, True)])
async def _docs(ctx: discord_slash.SlashContext, text: str):
    await ctx.respond()
    base_url = "https://discord-py-slash-command.readthedocs.io/en/latest/"
    resp = await sphinx_parser.search_from_sphinx(base_url+"genindex.html", text)
    if not resp:
        return await ctx.send(content="No result found.")
    base_embed = discord.Embed(title="Document Search", color=discord.Color.from_rgb(225, 225, 225))
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
            page_embed.add_field(name=str(count), value=f"[`{x.split('#')[1]}`]({link})", inline=False)
        except IndexError:
            continue
        resp.remove(x)
        count += 1
    embed_list.append(page_embed)
    if not embed_list:
        return await ctx.send(content="No result found.")
    await page.start_page(bot, ctx, embed_list, embed=True)


bot.loop.create_task(init_tags())

bot.run(get_settings("token"))
