import collections
import typing
from pathlib import Path

import interactions as ipy
from interactions.ext import prefixed_commands as prefixed

from common.const import METADATA

__all__ = (
    "proficient_check",
    "proficient_only",
    "mod_check",
    "mods_only",
    "file_to_ext",
    "get_all_extensions",
    "error_send",
)


def _member_from_ctx(ctx: ipy.BaseContext):
    user = ctx.author

    if isinstance(user, ipy.User):
        guild = ctx.bot.get_guild(METADATA["guild"])
        if not guild:
            return None

        user = guild.get_member(user.id)
        if not user:
            return None

    return user


def proficient_check(ctx: ipy.BaseContext):
    user = _member_from_ctx(ctx)
    return (
        user.has_role(METADATA["roles"]["Proficient"])
        or user.has_role(METADATA["roles"]["Moderator"])
        if user
        else False
    )


def proficient_only() -> typing.Any:
    async def predicate(ctx: ipy.BaseContext):
        return proficient_check(ctx)

    return ipy.check(predicate)


def mod_check(ctx: ipy.BaseContext):
    user = _member_from_ctx(ctx)
    return user.has_role(METADATA["roles"]["Moderator"]) if user else False


def mods_only() -> typing.Any:
    async def predicate(ctx: ipy.BaseContext):
        return mod_check(ctx)

    return ipy.check(predicate)


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
    ctx: ipy.InteractionContext | prefixed.PrefixedContext,
    msg: str,
    color: ipy.Color,
):
    embed = ipy.Embed(description=msg, color=color)

    # prefixed commands being replied to looks nicer
    func_name = "send" if isinstance(ctx, ipy.InteractionContext) else "reply"
    func = getattr(ctx, func_name)

    kwargs: dict[str, typing.Any] = {"embeds": [embed]}

    if isinstance(ctx, ipy.InteractionContext):
        kwargs["ephemeral"] = not ctx.responded or ctx.ephemeral

    await func(**kwargs)
