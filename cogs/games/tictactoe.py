import asyncio
import copy
import enum
import math
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


class GameState(enum.IntEnum):
    empty = 0
    player = -1
    ai = +1


BoardTemplate = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def determine_board_state(components: list) -> typing.List[list]:
    """
    Extrapolate the current state of the game based on the components of a message
    :param components: The components object from a message
    :return: The test_board state
    :rtype: list[list]
    """
    board = copy.deepcopy(BoardTemplate)
    for i in range(3):
        for x in range(3):
            button = components[i]["components"][x]
            if button["style"] == 2:
                board[i][x] = GameState.empty
            elif button["style"] == 1:
                board[i][x] = GameState.player
            elif button["style"] == 4:
                board[i][x] = GameState.ai
    return board


def render_board(board: list, disable=False) -> list:
    """
    Converts the test_board into a visual representation using discord components
    :param board: The game test_board
    :param disable: Disable the buttons on the test_board
    :return: List[action-rows]
    """
    buttons = []
    for i in range(3):
        for x in range(3):
            if board[i][x] == GameState.empty:
                style = ButtonStyle.grey
            elif board[i][x] == GameState.player:
                style = ButtonStyle.blurple
            else:
                style = ButtonStyle.red
            buttons.append(
                manage_components.create_button(
                    style=style,
                    label="‎",
                    custom_id=f"tic_tac_toe_button||{i},{x}",
                    disabled=disable,
                )
            )
    return manage_components.spread_to_rows(*buttons, max_in_row=3)


def determine_win_state(board: list, player: GameState) -> bool:
    """
    Determines if the specified player has won
    :param board: The game test_board
    :param player: The player to check for
    :return: bool, have they won
    """
    win_states = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[2][0], board[1][1], board[0][2]],
    ]
    if [player, player, player] in win_states:
        return True
    return False


def determine_possible_positions(board: list) -> list:
    """
    Determines all the possible positions in the current game state
    :param board: The game test_board
    :return: A list of possible positions
    """
    possible_positions = []
    for i in range(3):
        for x in range(3):
            if board[i][x] == GameState.empty:
                possible_positions.append([i, x])
    return possible_positions


def evaluate(board):
    if determine_win_state(board, GameState.ai):
        score = +1
    elif determine_win_state(board, GameState.player):
        score = -1
    else:
        score = 0
    return score


def min_max(test_board: list, depth: int, player: GameState):
    if player == GameState.ai:
        best = [-1, -1, -math.inf]
    else:
        best = [-1, -1, +math.inf]

    if (
        depth == 0
        or determine_win_state(test_board, GameState.player)
        or determine_win_state(test_board, GameState.ai)
    ):
        score = evaluate(test_board)
        return [-1, -1, score]

    for cell in determine_possible_positions(test_board):
        x, y = cell[0], cell[1]
        test_board[x][y] = player
        score = min_max(test_board, depth - 1, -player)
        test_board[x][y] = GameState.empty
        score[0], score[1] = x, y

        if player == GameState.ai:
            if score[2] > best[2]:
                best = score
        else:
            if score[2] < best[2]:
                best = score
    return best


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
            content=f"{ctx.author.mention}'s tic tac toe game",
            components=render_board(copy.deepcopy(BoardTemplate)),
        )

    def determine_board_state(self, components: list):
        board = []
        for i in range(3):
            row = components[i]["components"]
            for button in row:
                if button["style"] == 2:
                    board.append(GameState.empty)
                elif button["style"] == 1:
                    board.append(GameState.player)
                elif button["style"] == 4:
                    board.append(GameState.ai)

        return board

    @cog_component(components=render_board(board=copy.deepcopy(BoardTemplate)))
    async def process_turn(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        try:
            if ctx.author.id != ctx.origin_message.mentions[0].id:
                return
        except:
            return
        button_pos = (ctx.custom_id.split("||")[-1]).split(",")
        button_pos = [int(button_pos[0]), int(button_pos[1])]
        components = ctx.origin_message.components

        _board = determine_board_state(components)

        if _board[button_pos[0]][button_pos[1]] == GameState.empty:
            _board[button_pos[0]][button_pos[1]] = GameState.player
            if not determine_win_state(_board, GameState.player):
                # ai pos
                if len(determine_possible_positions(_board)) != 0:
                    depth = len(determine_possible_positions(_board))

                    move = await asyncio.to_thread(
                        min_max, copy.deepcopy(_board), depth, GameState.ai
                    )
                    x, y = move[0], move[1]
                    _board[x][y] = GameState.ai
        else:
            return

        if determine_win_state(_board, GameState.player):
            winner = ctx.author.mention
        elif determine_win_state(_board, GameState.ai):
            winner = self.bot.user.mention
        elif len(determine_possible_positions(_board)) == 0:
            winner = "Nobody"
        else:
            winner = None

        _board = render_board(_board, disable=winner is not None)

        await ctx.edit_origin(
            content=f"{ctx.author.mention}'s tic tac toe game"
            if not winner
            else f"{winner} has won!",
            components=manage_components.spread_to_rows(*_board, max_in_row=3),
        )


def setup(bot: commands.Bot):
    print("Loading tic tac toe")
    bot.add_cog(TicTacToe(bot))
