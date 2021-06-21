from discord.ext import commands

from modules.get_settings import get_settings

guild_ids = get_settings("servers")


class Buttons(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.load_extension("cogs.games.tictactoe")


def setup(bot: commands.Bot):
    bot.add_cog(Buttons(bot))
