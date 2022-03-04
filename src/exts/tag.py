import interactions
import json
import logging

log = logging.getLogger("astro.exts.tag")

class Tag(interactions.Extension):
    """An extension dedicated to /tag."""

    def __init__(self, bot):
        self.bot = bot
        self.edited_name = None

    @interactions.extension_command(
        name="tag",
        description="Handles \"tags\" aka. pre-written feeds for help.",
        scope=789032594456576001,
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
                options=[],
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
        self, ctx: interactions.CommandContext, sub_command: str=None, name: str=None
    ):
        log.debug("We've detected /tag, matching...")

        match sub_command:
            case "view":
                await self._view_tag(ctx, name)
            case "edit":
                await self._edit_tag(ctx, name)
            case "delete":
                await self._delete_tag(ctx, name)
            case _:
                await self._create_tag(ctx)


    async def _view_tag(self, ctx: interactions.CommandContext, name: str):
        """Views a tag that currently exists within the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for view. Returning result...")

        if db.get(name):
            await ctx.send(db[name])
        else:
            await ctx.send(f":x: Tag `{name}` does not exist.", ephemeral=True)

    async def _create_tag(self, ctx: interactions.CommandContext):
        """Creates a tag and adds it into the database."""
        log.debug("Matched for create. Returning result...")

        if not self.__check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        else:
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

    async def _edit_tag(self, ctx: interactions.CommandContext, name: str):
        """Edits a tag that currently exists within the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for edit. Returning result...")

        if not self.__check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        else:
            if name in db:
                modal = interactions.Modal(
                    title="Edit tag",
                    custom_id="edit_tag",
                    components=[
                        interactions.TextInput(
                            style=interactions.TextStyleType.PARAGRAPH,
                            label="What do you want the tag to include?",
                            value=db[name],
                            placeholder="(Note: you can also put codeblocks in here!)",
                            custom_id="new_tag_description",
                        ),
                    ],
                )
                self.edited_name = name

                await ctx.popup(modal)
            else:
                await ctx.send(f":x: Tag `{name}` does not exist.", ephemeral=True)

    async def _delete_tag(self, ctx: interactions.CommandContext, name: str):
        """Deletes a tag that currently exists within the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for delete. Returning result...")

        if not self.__check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        else:
            if name in db:
                del db[name]
                db = open("./db/tags.json", "w").write(json.dumps(db))

                await ctx.send(
                    f":heavy_check_mark: Tag `{name}` has been successfully deleted.",
                    ephemeral=True
                )
            else:
                await ctx.send(f":x: Tag `{name}` does not exist.", ephemeral=True)

    def __check_role(self, ctx: interactions.CommandContext) -> bool:
        """Checks whether an invoker has the Helper role or not."""
        # TODO: please get rid of me when perms v2 is out. this is so dumb.
        return bool("818861272484806656" in [str(role) for role in ctx.author.roles])

    @interactions.extension_autocomplete(command=949191547709173802, name="name")
    async def __parse_tag(self, ctx: interactions.CommandContext, name: str=""):
        """Parses the current choice you're making with /tag."""
        letters: list = list(name) if name != "" else []
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Autocompleting tag query for choices...")

        if not letters:
            await ctx.populate([interactions.Choice(name=tag, value=tag) for tag in (db[:24] if len(db) > 25 else db)])
        else:
            choices: list = []

            for tag in db:
                focus: str = "".join(letters)

                if focus.lower() in tag.lower() and len(choices) < 26:
                    choices.append(interactions.Choice(name=tag, value=tag))

            await ctx.populate(choices)
            
    @interactions.extension_modal(modal="new_tag")
    async def __new_tag(self, ctx: interactions.CommandContext, name: str, description: str):
        """Creates a new tag through the modal UI."""
        db = json.loads(open("./db/tags.json", "r").read())

        if name not in db:
            db.update({name: description})
            db = open("./db/tags.json", "w").write(json.dumps(db))

            await ctx.send(
                f":heavy_check_mark: `{name}` now exists. In order to view it, please use `/tag view`.",
                ephemeral=True
            )
        else:
            await ctx.send(
                ":x: Tag `{name}` already exists.\n(Did you mean to use `/tag edit`?)",
                ephemeral=True
            )

    @interactions.extension_modal(modal="edit_tag")
    async def __edit_tag(self, ctx: interactions.CommandContext, description: str):
        """Creates a new tag through the modal UI."""
        db = json.loads(open("./db/tags.json", "r").read())
        db.update({self.edited_name: description})
        db = open("./db/tags.json", "w").write(json.dumps(db))

        await ctx.send(
            f":heavy_check_mark: Tag `{self.edited_name}` has been edited.",
            ephemeral=True
        )

def setup(bot):
    Tag(bot)