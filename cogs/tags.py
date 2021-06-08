import typing

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands

guild_ids = [789032594456576001]


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.tag_opt = manage_commands.create_option("reply_to", "Message ID to reply.", 3, False)

        self.bot.loop.create_task(self.init_tags())

    async def template(self, ctx: SlashContext, tag_id: typing.Optional[str] = None):
        """
        The base function of tags

        :param ctx: SlashContext
        :param tag_id: the tags id
        :return:
        """
        resp = await self.bot.db.res_sql(
            """SELECT value FROM tags WHERE cmd_id=?""", (ctx.command_id,)
        )
        content = resp[0]["value"]
        if tag_id:
            try:
                msg: discord.Message = await ctx.channel.fetch_message(int(tag_id))
                await ctx.send("Message found, replying", hidden=True)
                return await msg.reply(content)
            except (
                discord.Forbidden,
                discord.HTTPException,
                discord.NotFound,
                TypeError,
                ValueError,
            ):
                await ctx.send("Couldn't find message to reply. Normally sending tag.", hidden=True)
        await ctx.send(content)

    async def init_tags(self):
        await self.bot.wait_until_ready()
        tags = await self.bot.db.res_sql("""SELECT * FROM tags""")
        for x in tags:
            owner = self.bot.get_user(int(x["user"]))
            owner = str(owner) if owner else "unknown user"
            self.bot.slash.add_slash_command(
                self.template,
                x["name"],
                guild_ids=guild_ids,
                options=[self.tag_opt],
                description=f"Custom tag by {owner}.",
            )
        await self.bot.slash.sync_all_commands()
        cmds = await manage_commands.get_all_commands(
            self.bot.user.id, self.bot.http.token, guild_ids[0]
        )
        for x in cmds:
            print(f"updating {x['name']}")
            cmd_id = x["id"]
            cmd_name = x["name"]
            if cmd_name in ["tag", "subscribe", "unsubscribe"]:
                continue
            await self.bot.db.exec_sql(
                """UPDATE tags SET cmd_id=? WHERE name=?""", (cmd_id, cmd_name)
            )

    @cog_ext.cog_subcommand(
        base="tag",
        name="add",
        guild_ids=guild_ids,
        description="Adds a new tag.",
        options=[
            {
                "name": "name",
                "description": "Name of the tag.",
                "type": 3,
                "required": True,
            },
            {
                "name": "response",
                "description": "Response of the tag.",
                "type": 3,
                "required": True,
            },
        ],
    )
    async def _tag_add(self, ctx: SlashContext, name: str, response: str):
        is_exist = await self.bot.db.res_sql("""SELECT * FROM tags WHERE name=?""", (name,))
        if is_exist or name in self.bot.slash.commands.keys():
            return await ctx.send("Uh oh. That name already exists.", hidden=True)
        if len(name) < 3:
            return await ctx.send("Name should be at least 3 characters or longer.", hidden=True)
        resp = await manage_commands.add_slash_command(
            self.bot.user.id,
            self.bot.http.token,
            ctx.guild_id,
            name,
            f"Custom tag by {ctx.author}.",
            options=[self.tag_opt],
        )
        cmd_id = resp["id"]
        await self.bot.db.exec_sql(
            """INSERT INTO tags VALUES (?, ?, ?, ?)""",
            (name, response, ctx.author_id, cmd_id),
        )

        self.bot.slash.add_slash_command(
            self.template, name, guild_ids=[ctx.guild_id], options=[self.tag_opt]
        )
        await ctx.send(f"Successfully added tag `{name}`!", hidden=True)

    @cog_ext.cog_subcommand(
        base="tag",
        name="remove",
        guild_ids=guild_ids,
        description="Removes existing tag.",
        options=[
            {
                "name": "name",
                "description": "Name of the tag.",
                "type": 3,
                "required": True,
            }
        ],
    )
    async def _tag_remove(self, ctx: SlashContext, name: str):
        resp = await self.bot.db.res_sql(
            """SELECT cmd_id FROM tags WHERE name=? AND user=?""", (name, ctx.author_id)
        )
        if ctx.author_id == 174918559539920897:
            resp = await self.bot.db.res_sql("""SELECT cmd_id FROM tags WHERE name=?""", (name,))
        if not resp:
            return await ctx.send("Tag not found. Check tag name.", hidden=True)
        await manage_commands.remove_slash_command(
            self.bot.user.id, self.bot.http.token, ctx.guild_id, resp[0]["cmd_id"]
        )
        await self.bot.db.exec_sql("""DELETE FROM tags WHERE cmd_id=?""", (resp[0]["cmd_id"],))
        del self.bot.slash.commands[name]
        await ctx.send(f"Successfully removed tag `{name}`!", hidden=True)


def setup(bot: commands.Bot):
    bot.add_cog(Tags(bot))
