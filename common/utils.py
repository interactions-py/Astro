import collections
import typing
from pathlib import Path

import naff

from common.const import METADATA


def helpers_only() -> typing.Any:
    async def predicate(ctx: naff.Context):
        return isinstance(ctx.author, naff.Member) and ctx.author.has_role(
            METADATA["roles"]["Helper"], METADATA["roles"]["Moderator"]
        )

    return naff.check(predicate)


def mods_only() -> typing.Any:
    async def predicate(ctx: naff.Context):
        return isinstance(ctx.author, naff.Member) and ctx.author.has_role(
            METADATA["roles"]["Moderator"]
        )

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
