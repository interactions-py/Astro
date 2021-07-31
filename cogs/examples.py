from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
)


class Examples(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="example", name="slash", description="Example slash command")
    async def example_slash(self, ctx: SlashContext):
        await ctx.send("Test")  # Sends "Test"

    @cog_ext.cog_subcommand(base="example", name="buttons", description="Example buttons")
    async def example_buttons(self, ctx: SlashContext):
        buttons = [
            create_button(
                style=ButtonStyle.primary,  # what colo[u]r (except URL)
                label="Primary/Blue/Blurple",  # what it displays
                custom_id="Primary/Blue/Blurple",  # its component id
            ),
            create_button(
                style=ButtonStyle.secondary,
                label="Secondary/Gr[a|e]y",
                custom_id="Secondary/Gr[a|e]y",
            ),
            create_button(
                style=ButtonStyle.success, label="Success/Green", custom_id="Success/Green"
            ),
            create_button(style=ButtonStyle.danger, label="Danger/Red", custom_id="Danger/Red"),
            create_button(
                style=ButtonStyle.URL,
                label="URL",
                url="https://discord-py-slash-command.readthedocs.io/en/latest/components.html",
            ),
        ]
        action_row = create_actionrow(*buttons)  # creates action row of 5 buttons
        await ctx.send("All of the buttons:", components=[action_row])

    @cog_ext.cog_subcommand(base="example", name="select", description="Example select")
    async def example_select(self, ctx: SlashContext):
        select = create_select(
            options=[  # the options in your dropdown
                create_select_option("Lab Coat", value="Lab Coat", emoji="🥼"),
                create_select_option("Test Tube", value="Test Tube", emoji="🧪"),
                create_select_option("Petri Dish", value="Petri Dish", emoji="🧫"),
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=2,  # the maximum number of options a user can select
            custom_id="select",
        )
        await ctx.send(
            "Example select:", components=[create_actionrow(select)]
        )  # like action row with buttons but without * in front of the variable

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        if ctx.component_type == 2:  # button
            await ctx.send(f"You pressed {ctx.custom_id}!", hidden=True)
        else:  # select
            string = (
                " and ".join(ctx.selected_options)
                if len(ctx.selected_options) > 1
                else "".join(ctx.selected_options)
            )
            await ctx.send(f"You selected {string}!", hidden=True)


def setup(bot):
    bot.add_cog(Examples(bot))
