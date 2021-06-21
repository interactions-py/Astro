import asyncio
import random
import typing

import discord
import discord_slash.model
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.cog_ext import cog_component
from discord_slash.utils import manage_commands, manage_components
from discord_slash.model import ButtonStyle

from modules.get_settings import get_settings

guild_ids = get_settings("servers")


def create_board() -> list:
    """Creates the tic tac toe board"""
    buttons = []
    for i in range(9):
        buttons.append(
            manage_components.create_button(
                style=ButtonStyle.grey, label="‎", custom_id=f"tic_tac_toe_button||{i}"
            )
        )
    action_rows = manage_components.spread_to_rows(*buttons, max_in_row=3)
    return action_rows


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @cog_ext.cog_subcommand(
        base="tic_tac_toe",
        name="start",
        description="Start a game of tic tac toe",
        guild_ids=guild_ids,
    )
    async def ttt_start(self, ctx: SlashContext):
        await ctx.send(
            content=f"{ctx.author.mention}'s tic tac toe game", components=create_board()
        )

    def determine_board_state(self, components: list):
        board = []
        for i in range(3):
            row = components[i]["components"]
            for button in row:
                if button["style"] == 2:
                    board.append("empty")
                elif button["style"] == 1:
                    board.append("player")
                elif button["style"] == 4:
                    board.append("enemy")

        return board

    def determine_win_state(self, board: list):
        if board[0] == board[1] == board[2] != "empty":  # row 1
            return board[0]
        if board[3] == board[4] == board[5] != "empty":  # row 2
            return board[3]
        if board[6] == board[7] == board[8] != "empty":  # row 3
            return board[6]
        if board[0] == board[3] == board[6] != "empty":  # col 1
            return board[0]
        if board[1] == board[4] == board[7] != "empty":  # col 2
            return board[1]
        if board[2] == board[5] == board[8] != "empty":  # col 3
            return board[2]
        if board[0] == board[4] == board[8] != "empty":  # diag 1
            return board[0]
        if board[2] == board[4] == board[6] != "empty":  # diag 2
            return board[2]
        return None

    @cog_component(components=create_board())
    async def process_turn(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        try:
            if ctx.author.id != ctx.origin_message.mentions[0].id:
                return
        except:
            return
        button_pos = int(ctx.custom_id.split("||")[-1])
        components = ctx.origin_message.components

        board = self.determine_board_state(components)

        if board[button_pos] == "empty":
            board[button_pos] = "player"

            # ai pos
            if board.count("empty") != 0:
                while True:
                    pos = random.randint(0, 8)
                    if board[pos] == "empty":
                        board[pos] = "enemy"
                        break
                    await asyncio.sleep(0)
        else:
            return

        winner = self.determine_win_state(board)
        if winner:
            winner = ctx.author.mention if winner == "player" else self.bot.user.mention

        if not winner:
            if board.count("empty") == 0:
                winner = "Nobody"

        # convert the board in buttons
        for i in range(9):
            style = (
                ButtonStyle.grey
                if board[i] == "empty"
                else ButtonStyle.blurple
                if board[i] == "player"
                else ButtonStyle.red
            )
            board[i] = manage_components.create_button(
                style=style,
                label="‎",
                custom_id=f"tic_tac_toe_button||{i}",
                disabled=True if winner else False,
            )

        await ctx.edit_origin(
            content=f"{ctx.author.mention}'s tic tac toe game"
            if not winner
            else f"{winner} has won!",
            components=manage_components.spread_to_rows(*board, max_in_row=3),
        )


def setup(bot: commands.Bot):
    print("Loading tic tac toe")
    bot.add_cog(TicTacToe(bot))
