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


class Language(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @cog_ext.cog_slash(
        name="set-language",
        description="Set your language in this server",
        guild_ids=guild_ids,
        options=[
            manage_commands.create_option(
                name="language",
                description="The language you wish to choose",
                option_type=int,
                required=True,
                choices=[
                    manage_commands.create_choice(value=1, name="한국어 | Korean"),
                    manage_commands.create_choice(value=2, name="русский | Russian"),
                    manage_commands.create_choice(value=3, name="Deutsche | German"),
                    manage_commands.create_choice(value=4, name="Français | French"),
                    manage_commands.create_choice(value=5, name="हिंदी | Hindi")
                ],
            )
        ],
    )
    async def set_language(self, ctx: SlashContext, language: int):
        if language == 1:
            role_id = get_settings("korean_role")
            message = '"한국어" 역할이 주어졌습니다'
        elif language == 2:
            role_id = get_settings("russian_role")
            message = 'Вам была выдана роль "Русский"'
        elif language == 3:
            role_id = get_settings("german_role")
            message = "Sie haben die deutsche Rolle bekommen"
        elif language == 4:
            role_id = get_settings("french_role")
            message = "Vous avez le rôle Français"
        elif lanuage == 5:
            role_id = get_settings("hindi_role")
            message = "अब आपके पास हिंदी की भूमिका है।"
        else:
            # shouldn't be possible, but just in case
            return await ctx.send("Sorry, that language choice wasn't recognised", hidden=True)
        role = ctx.guild.get_role(int(role_id))
        try:
            await ctx.author.add_roles(role, reason="Language role request")
            await ctx.send(message, hidden=True)
        except Exception as e:
            print(e)
            return await ctx.send(
                "Sorry, your role could not be applied, please try again later",
                hidden=True,
            )

    @cog_ext.cog_slash(
        name="remove-language",
        description="Remove your language related roles",
        guild_ids=guild_ids,
    )
    async def remove_language(self, ctx):
        await ctx.defer(hidden=True)
        role_ids = [
            get_settings("korean_role"),
            get_settings("german_role"),
            get_settings("russian_role"),
            get_settings("french_role"),
            get_settings("hindi_role")
        ]
        try:
            for role in ctx.author.roles:
                if role.id in role_ids:
                    await ctx.author.remove_roles(role)
            await ctx.send("Any language roles you had have now been removed", hidden=True)
        except:
            await ctx.send("Failed to remove roles... please try again later", hidden=True)


def setup(bot: commands.Bot):
    bot.add_cog(Language(bot))
