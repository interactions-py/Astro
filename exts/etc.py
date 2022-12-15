import importlib

import naff

import common.utils as utils
from common.const import METADATA


async def check_archive(ctx: naff.Context):
    return ctx.channel.id == METADATA["channels"]["help"]


class Etc(naff.Extension):
    @naff.slash_command("archive", description="Archives a help thread.")
    @utils.helpers_only()
    @naff.check(check_archive)  # type: ignore
    async def archive(self, ctx: naff.InteractionContext):
        await ctx.send("Archiving...")
        await ctx.channel.edit(archived=True, locked=True)


def setup(bot):
    importlib.reload(utils)
    Etc(bot)
