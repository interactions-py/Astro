import importlib
import re
from contextlib import suppress

import interactions as ipy
from interactions.ext import prefixed_commands as prefixed

import common.utils as utils
from common.const import *

TOKEN_REG = re.compile(r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27,}")


async def mod_check_wrapper(ctx: ipy.BaseContext) -> bool:
    return utils.mod_check(ctx)


class Etc(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.bot = bot

    @prefixed.prefixed_command()
    @ipy.check(mod_check_wrapper)
    async def sync(self, ctx: prefixed.PrefixedContext):
        await self.bot.synchronise_interactions(scopes=[METADATA["guild"], 0], delete_commands=True)
        await ctx.reply(":white_check_mark: Synchronized commands.")

    @ipy.listen()
    async def on_message_create(self, event: ipy.events.MessageCreate):
        message = event.message
        if message.content and TOKEN_REG.search(message.content):
            await message.reply(
                "Careful with your token! It looks like you leaked it. :eyes:",
                delete_after=30,
            )
            with suppress(ipy.errors.Forbidden, ipy.errors.NotFound):
                await message.delete()


def setup(bot: ipy.Client):
    importlib.reload(utils)
    Etc(bot)
