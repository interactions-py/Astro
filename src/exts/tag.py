import interactions

class Tag(interactions.Extension):
    """An extension dedicated to /tag."""

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="tag",
        description="Handles \"tags\" aka. pre-written feeds for help.",
        options=[
            interactions.Option(
                type=interactions.OptionType.SUB_COMMAND,
                name="view",
                description="Views an existing tag.",
                options=[
                    interactions.Option(
                        type=interactions.OptionType.STRING,
                        name="name",
                        description="The name of the tag you wish to view.",
                        required=True,
                        autocomplete=True,
                    ),
                ],
            ),
            interactions.Option(
                type=interactions.OptionType.SUB_COMMAND,
                name="create",
                description="Creates a new tag.",
                options=[
                    interactions.Option(
                        type=interactions.OptionType.STRING,
                        name="name",
                        description="The name of the tag you wish to create.",
                        required=True,
                        autocomplete=True,
                    ),
                ],
            ),
            interactions.Option(
                type=interactions.OptionType.SUB_COMMAND,
                name="edit",
                description="Edits an existing tag.",
                options=[
                    interactions.Option(
                        type=interactions.OptionType.STRING,
                        name="name",
                        description="The name of the tag you wish to edit.",
                        required=True,
                        autocomplete=True,
                    ),
                ],
            ),
            interactions.Option(
                type=interactions.OptionType.SUB_COMMAND,
                name="delete",
                description="Deletes an existing tag.",
                options=[
                    interactions.Option(
                        type=interactions.OptionType.STRING,
                        name="name",
                        description="The name of the tag you wish to delete.",
                        required=True,
                        autocomplete=True,
                    ),
                ],
            ),
        ],
    )
    async def tag(
        self, ctx: interactions.CommandContext, view=None, create=None, edit=None, delete=None
    ):
        if view:
            await self._view_tag(ctx)
        elif create:
            await self._create_tag(ctx)
        elif edit:
            await self._edit_tag(ctx)
        elif delete:
            await self._delete_tag(ctx)

    async def _view_tag(self, ctx: interactions.CommandContext):
        """Views a tag that currently exists within the database."""
        # TODO: code retrieval from database
        await ctx.send("This is the tag we want to send. :grin:")

    async def _create_tag(self, ctx: interactions.CommandContext):
        """Creates a tag and adds it into the database if one does not exist."""
        # TODO: code retrieval from database
        name: str = "foo"
        modal = interactions.Modal(
            title="Create new tag",
            custom_id="new_tag",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="What do you want the tag to be named?",
                    placeholder="d.py cogs vs. i.py extensions",
                    custom_id="new_tag_name",
                    max_length=100,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    label="What do you want the tag to include?",
                    placeholder="(Note: you can also put codeblocks in here!)",
                    custom_id="new_tag_description",
                ),
            ],
        )
        await ctx.popup(modal)

    async def _edit_tag(self, ctx: interactions.CommandContext):
        """Edits a tag that currently exists within the database."""
        # TODO: code retrieval from database
        name: str = "foo"
        modal = interactions.Modal(
            title="Edit tag",
            custom_id="edit_tag",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    label="What do you want the tag to include?",
                    placeholder="(Note: you can also put codeblocks in here!)",
                    custom_id="new_tag_description",
                ),
            ],
        )
        await ctx.popup(modal)

    async def _delete_tag(self, ctx: interactions.CommandContext):
        """Deletes a tag that currently exists within the database."""
        # TODO: code retrieval from database
        # TODO: check if the tag name exists
        # TODO: delete based on condition of existence
        existing_names: list[str] = ["foo", "bar", "baz"]
        name: str = "foo"

        if name in existing_names:
            await ctx.send(f"Tag {name} has been successfully deleted.")

    @interactions.extension_autocomplete(command=947722281440915517, name="name")
    async def __parse_tag(self, ctx: interactions.CommandContext, name: str=""):
        """Parses the current choice you're making with /tag."""
        letters = list(name) if name != "" else []

        if letters != []:
            # TODO: code regex check with a startswith to the database entries.
            ...
            
    @interactions.extension_modal(modal="new_tag")
    async def __new_tag(self, ctx: interactions.CommandContext):
        """Creates a new tag through the modal UI."""
        # TODO: code writing to database
        # TODO: check if the tag name exists
        bad_names: list[str] = ["bar", "baz"]
        name: str = "foo"

        if name not in bad_names:
            await ctx.send(
                f":heavy_check_mark: `{name}` now exists. In order to view it, please use `/tag view`.",
                ephemeral=True
            )

    @interactions.extension_modal(modal="edit_tag")
    async def __edit_tag(self, ctx: interactions.CommandContext):
        """Creates a new tag through the modal UI."""
        # TODO: code writing to database
        name: str = "foo"
        await ctx.send(
            f":heavy_check_mark: `{name}` has been edited. In order to view the new changes, please use `/tag view`.",
            ephemeral=True
        )

def setup(bot):
    Tag(bot)