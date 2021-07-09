import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils import manage_components
from discord_slash.cog_ext import cog_component
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
from discord_slash.model import ButtonStyle

class Examples(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="example",
                            name="slash",
                            description="Example slash command")
    async def example_slash(self, ctx: SlashContext):
        await ctx.send("Test") # Sends "Test"
    
    @cog_ext.cog_subcommand(base="example",
                            name="buttons",
                            description="Example buttons")
    async def example_buttons(self, ctx: SlashContext):
        buttons = [
            create_button(
                style=ButtonStyle.primary,
                label="Primary/Blue/Blurple",
                custom_id="button"
            ),
            create_button(
                style=ButtonStyle.secondary,
                label="Secondary/Gr[a|e]y",
                custom_id="button"
            ),
            create_button(
                style=ButtonStyle.success,
                label="Success/Green",
                custom_id="button"
            ),
            create_button(
                style=ButtonStyle.danger,
                label="Danger/Red",
                custom_id="button"
            ),
            create_button(
                style=ButtonStyle.URL,
                label="URL",
                url="https://discord-py-slash-command.readthedocs.io/en/latest/components.html",
                custom_id="button"
            )
        ]
        action_row = create_actionrow(*buttons)
        await ctx.send("All of the buttons:", components=[action_row])
    
    @cog_ext.cog_subcommand(base="example",
                            name="select",
                            description="Example select")
    async def example_select(self, ctx: SlashContext):
        select = create_select(
            options=[# the options in your dropdown
                create_select_option("Lab Coat", value="coat", emoji="🥼"),
                create_select_option("Test Tube", value="tube", emoji="🧪"),
                create_select_option("Petri Dish", value="dish", emoji="🧫"),
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=2,  # the maximum number of options a user can select
            custom_id="select"
        )
        await ctx.send("Example select:", components=[create_actionrow(select)])  # like action row with buttons but without * in front of the variable
    
    @cog_ext.cog_component()
    async def button(self, ctx: ComponentContext):
        await ctx.send("You pressed a button!", hidden=True)
    
    @cog_ext.cog_component()
    async def select(self, ctx: ComponentContext):
        await ctx.send("You used a select!", hidden=True)

def setup(bot):
    bot.add_cog(Examples(bot))