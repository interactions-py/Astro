import discord
import asyncio
from discord.ext import commands
from discord_slash import SlashContext


async def start_page(bot: commands.Bot, ctx: SlashContext, lists: list, time: int = 30, embed: bool = False):
    counts = len(lists) - 1

    emoji_list = ["⬅", "⏹", "➡"]

    if embed is True:
        msg = await ctx.channel.send(embed=lists[0])
    else:
        msg = await ctx.channel.send(lists[0])
    counted = 0

    for x in emoji_list:
        await msg.add_reaction(x)

    try:
        while True:
            reaction = (await bot.wait_for("reaction_add", timeout=time, check=lambda r, u: r.message.id == msg.id and str(r.emoji) in emoji_list and u.id == ctx.author.id))[0]
            if str(reaction.emoji) == emoji_list[1]:
                try:
                    await msg.clear_reactions()
                except discord.Forbidden:
                    await msg.remove_reaction(emoji_list[0], msg.author)
                    await msg.remove_reaction(emoji_list[1], msg.author)
                    await msg.remove_reaction(emoji_list[2], msg.author)
                break
            elif str(reaction.emoji) == emoji_list[2]:
                try:
                    await msg.remove_reaction(emoji_list[2], ctx.author)
                except discord.Forbidden:
                    pass
                counted += 1
                if counted > counts:
                    counted = 0
                if embed is True:
                    await msg.edit(embed=lists[counted])
                else:
                    await msg.edit(content=lists[counted])
            elif str(reaction.emoji) == emoji_list[0]:
                try:
                    await msg.remove_reaction(emoji_list[0], ctx.author)
                except discord.Forbidden:
                    pass
                counted -= 1
                if counted < 0:
                    counted = counts
                if embed is True:
                    await msg.edit(embed=lists[counted])
                else:
                    await msg.edit(content=lists[counted])
    except asyncio.TimeoutError:
        await ctx.channel.send("Timeout.", delete_after=5)
        try:
            await msg.clear_reactions()
        except discord.Forbidden:
            await msg.remove_reaction(emoji_list[0], msg.author)
            await msg.remove_reaction(emoji_list[1], msg.author)
            await msg.remove_reaction(emoji_list[2], msg.author)
        return
