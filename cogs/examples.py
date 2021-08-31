from discord.ext import commands
from discord_slash import cog_ext, SlashContext, MenuContext
from discord_slash.model import ButtonStyle, ContextMenuType
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
    wait_for_component,
)
from asyncio import TimeoutError


class Examples(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="example", name="slash", description="Example slash command"
    )
    async def example_slash(self, ctx: SlashContext):
        await ctx.send("Test")  # Sends "Test"

    @cog_ext.cog_subcommand(
        base="example", name="buttons", description="Example buttons"
    )
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
                style=ButtonStyle.success,
                label="Success/Green",
                custom_id="Success/Green",
            ),
            create_button(
                style=ButtonStyle.danger, label="Danger/Red", custom_id="Danger/Red"
            ),
            create_button(
                style=ButtonStyle.URL,
                label="URL",
                url="https://discord-interactions.readthedocs.io/en/latest/components.html",
            ),
        ]
        action_row = create_actionrow(*buttons)  # creates action row of 5 buttons
        msg = await ctx.send("All of the buttons:", components=[action_row])
        while True:
            try:
                button_ctx = await wait_for_component(
                    self.bot, components=action_row, timeout=60
                )
                if button_ctx.component_type == 2:  # check if button
                    await button_ctx.send(
                        f"You pressed {button_ctx.custom_id}!", hidden=True
                    )
            except TimeoutError:
                for i in range(4):
                    action_row["components"][i]["disabled"] = True
                await msg.edit(content="Timed out.", components=[action_row])
                break

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
        ar = create_actionrow(select)
        msg = await ctx.send(
            "Example select:", components=[ar]
        )  # like action row with buttons but without * in front of the variable
        while True:
            try:
                button_ctx = await wait_for_component(
                    self.bot, components=ar, timeout=60
                )
                string = (
                    " and ".join(button_ctx.selected_options)
                    if len(button_ctx.selected_options) > 1
                    else "".join(button_ctx.selected_options)
                )
                await button_ctx.send(f"You selected {string}!", hidden=True)
            except TimeoutError:
                ar["components"][0]["disabled"] = True
                await msg.edit(content="Timed out.", components=[ar])
                break

    @cog_ext.cog_context_menu(
        target=ContextMenuType.MESSAGE, name="Example Message Menu"
    )
    async def example_message_menu(self, ctx: MenuContext):
        await ctx.send(
            f"This is a test. BTW, I know what you said. :)\n||{ctx.target_message.clean_content}||"
        )

    @cog_ext.cog_context_menu(target=ContextMenuType.USER, name="Example User Menu")
    async def example_user_menu(self, ctx: MenuContext):
        await ctx.send(
            f"{ctx.author.display_name} used the context menu on {ctx.target_author.display_name}!"
        )


def setup(bot):
    bot.add_cog(Examples(bot))
