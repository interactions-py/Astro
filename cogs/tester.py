import asyncio
import re

import discord
import github.GithubException
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands
from github import Github

from modules.get_settings import get_settings

guild_ids = get_settings("servers")


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @cog_ext.cog_slash(
        name="join-unstable",
        description="Join the testers for the unstable branch.",
        guild_ids=guild_ids,
    )
    async def join_unstable(self, ctx: SlashContext):
        role_id = get_settings("tester_role")
        role = ctx.guild.get_role(int(role_id))
        try:
            await ctx.author.add_roles(role, reason="Tester role request")
            await ctx.send("Your tester role has been applied", hidden=True)
        except Exception as e:
            print(e)
            return await ctx.send(
                "Sorry, your role could not be applied, please try again later",
                hidden=True,
            )

    @cog_ext.cog_slash(
        name="leave-unstable",
        description="Leave from the testers of the unstable branch.",
        guild_ids=guild_ids,
    )
    async def remove_language(self, ctx):
        await ctx.defer(hidden=True)
        role_id = get_settings("tester_role")
        try:
            for role in ctx.author.roles:
                if role.id == role_id:
                    await ctx.author.remove_roles(role)
            await ctx.send("Your tester role has now been removed", hidden=True)
        except:
            await ctx.send("Failed to remove role... please try again later", hidden=True)


def setup(bot: commands.Bot):
    bot.add_cog(Tester(bot))
