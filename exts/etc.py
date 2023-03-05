import importlib
import re
from contextlib import suppress

import naff

import common.utils as utils
from common.const import *

TOKEN_REG = re.compile(r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27,}")


async def mod_check_wrapper(ctx: naff.Context):
    return utils.mod_check(ctx)


class Etc(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.bot = bot

    @naff.prefixed_command()
    async def sync(self, ctx: naff.PrefixedContext):
        async with ctx.channel.typing:
            await self.bot.synchronise_interactions(
                scopes=[METADATA["guild"], 0], delete_commands=True
            )
        await ctx.reply(":white_check_mark: Synchronized commands.")

    @naff.listen()
    async def on_message_create(self, event: naff.events.MessageCreate):
        message = event.message
        if message.content and TOKEN_REG.search(message.content):
            await message.reply(
                "Careful with your token! It looks like you leaked it. :eyes:",
                delete_after=30,
            )
            with suppress(naff.errors.Forbidden, naff.errors.NotFound):
                await message.delete()


def setup(bot: naff.Client):
    importlib.reload(utils)
    Etc(bot)
