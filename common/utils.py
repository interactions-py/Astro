import collections
import typing
from pathlib import Path

import naff

from common.const import METADATA


def _member_from_ctx(ctx: naff.Context):
    user = ctx.author

    if isinstance(user, naff.User):
        guild = ctx.bot.get_guild(METADATA["guild"])
        if not guild:
            return None

        user = guild.get_member(user.id)
        if not user:
            return None

    return user


def helper_check(ctx: naff.Context):
    user = _member_from_ctx(ctx)
    return (
        user.has_role(METADATA["roles"]["Helper"]) or user.has_role(METADATA["roles"]["Moderator"])
        if user
        else False
    )


def helpers_only() -> typing.Any:
    async def predicate(ctx: naff.Context):
        return helper_check(ctx)

    return naff.check(predicate)


def mod_check(ctx: naff.Context):
    user = _member_from_ctx(ctx)
    return user.has_role(METADATA["roles"]["Moderator"]) if user else False


def mods_only() -> typing.Any:
    async def predicate(ctx: naff.Context):
        return mod_check(ctx)

    return naff.check(predicate)


def file_to_ext(str_path, base_path):
    # changes a file to an import-like string
    str_path = str_path.replace(base_path, "")
    str_path = str_path.replace("/", ".")
    return str_path.replace(".py", "")


def get_all_extensions(str_path, folder="exts"):
    # gets all extensions in a folder
    ext_files = collections.deque()
    loc_split = str_path.split(folder)
    base_path = loc_split[0]

    if base_path == str_path:
        base_path = base_path.replace("main.py", "")
    base_path = base_path.replace("\\", "/")

    if base_path[-1] != "/":
        base_path += "/"

    pathlist = Path(f"{base_path}/{folder}").glob("**/*.py")
    for path in pathlist:
        str_path = str(path.as_posix())
        str_path = file_to_ext(str_path, base_path)

        if not str_path.startswith("_"):
            ext_files.append(str_path)

    return ext_files


async def error_send(
    ctx: naff.InteractionContext | naff.PrefixedContext | naff.HybridContext,
    msg: str,
    color: naff.Color,
):
    embed = naff.Embed(description=msg, color=color)

    # prefixed commands being replied to looks nicer
    func_name = "send" if isinstance(ctx, naff.InteractionContext) else "reply"
    func = getattr(ctx, func_name)

    kwargs: dict[str, typing.Any] = {"embeds": [embed]}

    if isinstance(ctx, (naff.InteractionContext, naff.HybridContext)):
        kwargs["ephemeral"] = not ctx.responded or ctx.ephemeral

    await func(**kwargs)
