import asyncio
from discord.ext import commands
from discord_slash import SlashContext
from random import randint
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    wait_for_component,
)


async def start_page(
    bot: commands.Bot,
    ctx: SlashContext,
    lists: list,
    time: int = 30,
    embed: bool = False,
):
    top = len(lists) - 1
    rand_num = randint(1, 10000)

    emoji_list = ["◀", "⏹", "▶"]

    buttons = [
        create_button(style=1, emoji=emoji_list[0], custom_id=f"prev{rand_num}"),
        create_button(style=1, emoji=emoji_list[1], custom_id=f"stop{rand_num}"),
        create_button(style=1, emoji=emoji_list[2], custom_id=f"next{rand_num}"),
    ]
    action_row = create_actionrow(*buttons)

    if embed is True:
        msg = await ctx.send(
            content=":arrow_down: Look here for results",
            embed=lists[0],
            components=[action_row],
        )
    else:
        msg = await ctx.send(lists[0], components=[action_row])

    counter = 0

    try:
        while True:
            button_ctx = await wait_for_component(
                bot,
                components=[f"prev{rand_num}", f"stop{rand_num}", f"next{rand_num}"],
                timeout=time,
            )
            if button_ctx.custom_id == f"prev{rand_num}":
                counter -= 1 if counter > 0 else 0
                await button_ctx.edit_origin(
                    embed=lists[counter]
                ) if embed else await button_ctx.edit_origin(content=lists[counter])
            elif button_ctx.custom_id == f"stop{rand_num}":
                await button_ctx.edit_origin(components=None)
                break
            elif button_ctx.custom_id == f"next{rand_num}":
                counter += 1 if counter < top else top
                await button_ctx.edit_origin(
                    embed=lists[counter]
                ) if embed else await button_ctx.edit_origin(content=lists[counter])
    except asyncio.TimeoutError:
        await ctx.channel.send("Timeout.", delete_after=5)
        await msg.edit(components=None)
        return
