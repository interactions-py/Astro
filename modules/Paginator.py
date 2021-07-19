import random
from asyncio import TimeoutError
from typing import Optional, Union

import discord
from discord.ext import commands

from discord_slash import SlashContext
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    wait_for_component,
)


async def Paginator(
    bot: commands.bot,
    ctx: SlashContext,
    pages: list[discord.Embed],
    content: Optional[str] = None,
    prevLabel: str = "Previous",
    nextLabel: str = "Next",
    prevEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = None,
    nextEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = None,
    indexStyle: Optional[Union[ButtonStyle, int]] = 1,
    prevStyle: Optional[Union[ButtonStyle, int]] = 3,
    nextStyle: Optional[Union[ButtonStyle, int]] = 3,
    timeout: Optional[int] = None,
    authorOnly: Optional[bool] = False,
):
    top = len(pages)  # limit of the paginator
    bid = random.randint(10000, 99999)  # base of button id
    index = 0  # starting page
    controlButtons = [
        # Previous Button
        create_button(
            style=prevStyle,
            label=prevLabel,
            custom_id=f"{bid}-prev",
            disabled=True,
            emoji=prevEmoji,
        ),
        # Index
        create_button(
            style=indexStyle,
            label=f"Page {index+1}/{top}",
            disabled=True,
            custom_id=f"{bid}-index",
        ),
        # Next Button
        create_button(
            style=nextStyle,
            label=nextLabel,
            custom_id=f"{bid}-next",
            disabled=False,
            emoji=nextEmoji,
        ),
    ]
    controls = create_actionrow(*controlButtons)
    await ctx.send(content=content, embed=pages[0], components=[controls])
    # handling the interaction
    tmt = True  # stop listening when timeout expires
    while tmt:
        try:
            button_context: ComponentContext = await wait_for_component(
                bot, components=[controls], timeout=timeout
            )
            await button_context.defer(edit_origin=True)
        except TimeoutError:
            tmt = False
            await ctx.message.edit(content=content, embed=pages[index], components=None)

        else:
            # Handling previous button
            if button_context.component_id == f"{bid}-prev" and index > 0:
                index = index - 1  # lowers index by 1
                if index == 0:
                    controls["components"][0]["disabled"] = True  # Disables the previous button
                controls["components"][2]["disabled"] = False  # Enables Next Button
                controls["components"][1]["label"] = f"Page {index+1}/{top}"  # updates the index
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=[controls]
                )
            # handling next button
            if button_context.component_id == f"{bid}-next" and index < top - 1:
                index = index + 1  # add 1 to the index
                if index == top - 1:
                    controls["components"][2]["disabled"] = True  # disables the next button
                controls["components"][0]["disabled"] = False  # enables previous button

                controls["components"][1]["label"] = f"Page {index+1}/{top}"  # updates the index
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=[controls]
                )
