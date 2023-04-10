from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
import os

import aiohttp
import interactions as ipy
from beanie import init_beanie
from interactions.ext import prefixed_commands
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

import common.utils as utils
from common.const import *
from common.models import Tag

logger = logging.getLogger("astro_bot")
logger.setLevel(logging.DEBUG)


stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.WARNING)
logger.addHandler(stderr_handler)

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

activity = ipy.Activity.create(name="you. 👀", type=ipy.ActivityType.WATCHING)

intents = ipy.Intents.new(
    guilds=True,
    guild_members=True,
    guild_moderation=True,
    guild_messages=True,
    direct_messages=True,
    message_content=True,
)

bot = ipy.Client(
    intents=intents,
    sync_interactions=False,
    debug_scope=METADATA["guild"],
    disable_dm_commands=True,
    status=ipy.Status.DO_NOT_DISTURB,
    activity=activity,
    fetch_members=True,
    send_command_tracebacks=False,
    logger=logger,
)
prefixed_commands.setup(bot)


async def start():
    client = AsyncIOMotorClient(os.environ["MONGO_DB_URL"], server_api=ServerApi("1"))
    await init_beanie(client.Astro, document_models=[Tag])  # type: ignore

    bot.session = aiohttp.ClientSession()

    ext_list = utils.get_all_extensions(SRC_PATH)

    for ext in ext_list:
        bot.load_extension(ext)

    try:
        await bot.astart(os.environ["TOKEN"])
    finally:
        await bot.session.close()


@ipy.listen("command_error", disable_default_listeners=True)
async def on_command_error(event: ipy.events.CommandError):
    # basically, this, compared to the built-in version:
    # - makes sure if the error can be sent ephemerally, it will
    # - only log the error if it isn't an "expected" error (check failure, cooldown, etc)
    # - send a message to the user if there's an unexpected error

    try:
        if isinstance(event.error, ipy.errors.CommandOnCooldown):
            await utils.error_send(
                event.ctx,
                msg=(
                    ":x: This command is on cooldown.\n"
                    f"Please try again in {int(event.error.cooldown.get_cooldown_time())} seconds."
                ),
                color=ASTRO_COLOR,
            )
        elif isinstance(event.error, ipy.errors.MaxConcurrencyReached):
            await utils.error_send(
                event.ctx,
                msg=(
                    ":x: This command has reached its maximum concurrent usage.\nPlease try again"
                    " shortly."
                ),
                color=ASTRO_COLOR,
            )
        elif isinstance(event.error, ipy.errors.CommandCheckFailure):
            await utils.error_send(
                event.ctx,
                msg=":x: You do not have permission to run this command.",
                color=ipy.BrandColors.YELLOW,
            )
        elif isinstance(event.error, ipy.errors.BadArgument):
            await utils.error_send(
                event.ctx,
                msg=f":x: {event.error}",
                color=ipy.MaterialColors.RED,
            )
        else:
            await utils.error_send(
                event.ctx,
                msg=(
                    ":x: An unexpected error has occured. The error will be logged and should be"
                    " fixed shortly."
                ),
                color=ipy.RoleColors.DARK_RED,
            )
            bot.dispatch(
                ipy.events.Error(
                    source=f"cmd `/{event.ctx.invoke_target}`",  # type: ignore
                    error=event.error,
                    args=event.args,
                    kwargs=event.kwargs,
                    ctx=event.ctx,
                )
            )
    except ipy.errors.LibraryException:
        bot.dispatch(
            ipy.events.Error(
                source=f"cmd `/{event.ctx.invoke_target}`",  # type: ignore
                error=event.error,
                args=event.args,
                kwargs=event.kwargs,
                ctx=event.ctx,
            )
        )


@ipy.listen("startup")
async def on_startup():
    print(f"Logged in as {bot.user.tag}.")


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Shutting down.")
