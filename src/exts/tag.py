import datetime
import interactions
import logging
import src.const
import src.model as model
from beanie import PydanticObjectId
from interactions.ext.paginator import Page, Paginator
from src.const import *

log = logging.getLogger("astro.exts.tag")


class Tag(interactions.Extension):
    """An extension dedicated to /tag."""

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(scope=METADATA["guild"])
    async def tag(self, *args, **kwargs):
        ...

    @tag.subcommand()
    @interactions.option("the name of the tag", autocomplete=True)
    async def view(self, ctx: interactions.CommandContext, tag_name: str):
        """Views a tag that currently exists within the database."""

        log.debug("Matched for view. Returning result...")

        if tag := await model.Tag.find_one(model.Tag.name == tag_name):
            await ctx.send(tag.description)
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    @tag.subcommand()
    @interactions.option("The name of the tag", autocomplete=True)
    async def info(self, ctx: interactions.CommandContext, tag_name: str):
        """Gathers information about a tag that currently exists within the database."""
        log.debug("Matched for info. Returning result...")

        if tag := await model.Tag.find_one(model.Tag.name == tag_name):
            embed = interactions.Embed(
                title='"' + tag_name + '"' if '"' not in tag_name else tag_name,
                color=0x5865F2,
                footer=interactions.EmbedFooter(
                    text=" ".join(
                        [
                            "Tags are made and maintained by the Helpers here in the support server.",
                            "Please contact one if you believe one is incorrect.",
                        ]
                    )
                ),
                fields=[
                    interactions.EmbedField(
                        name="Author",
                        value=f"<@{tag.author_id}>",
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="ID",
                        value=str(tag.id),
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="Timestamps",
                        value="\n".join(
                            [
                                f"Created: <t:{round(tag.created_at.timestamp())}:R>.",
                                "Last edited: "
                                + (
                                    f"<t:{round(tag.last_edited_at.timestamp())}:R>."
                                    if tag.last_edited_at
                                    else "N/A"
                                ),
                            ]
                        ),
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="Content", value="Please use `/tag view`."
                    ),
                ],
            )
            await ctx.send(embeds=embed)

    @tag.subcommand()
    async def list(self, ctx: interactions.CommandContext):
        """Lists all the tags existing in the database."""
        log.debug("Matched for list. Returning result...")

        _id: int = 0
        _pages: list = []
        _contents: list = []
        _embeds: list = []
        _value: str = ""

        def _divide(_list: list) -> list:
            for i in range(0, len(_list), 5):
                yield _list[i : i + 5]

        async for tag in model.Tag.find_all():
            _value += f"` {_id} ` {tag.name}\n"
            _id += 1

        for tag_group in _divide(_value.split("\n")):
            _contents.append(tag_group)

        for content in _contents:
            new_embed = interactions.Embed(
                title="Tag list",
                description="This is the list of currently existing tags.",
                color=0x5865F2,
            )
            new_embed.add_field(name="Names", value="\n".join(content))
            _embeds.append(new_embed)

        paginator = Paginator(
            client=self.client, ctx=ctx, pages=[Page(embeds=embed) for embed in _embeds], timeout=300,
        )

        await paginator.run()

    @tag.subcommand()
    async def create(self, ctx: interactions.CommandContext):
        """Creates a tag and adds it into the database."""
        log.debug("Matched for create. Returning result...")

        if not self._check_role(ctx):
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
                        max_length=2000,
                    ),
                ],
            )

            await ctx.popup(modal)
            await ctx.send("Modal sent.", ephemeral=True)

    @tag.subcommand()
    @interactions.option("The name of the tag", autocomplete=True)
    async def edit(self, ctx: interactions.CommandContext, tag_name: str):
        """Edits a tag that currently exists within the database."""
        log.debug("Matched for edit. Returning result...")

        if not self._check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        elif tag := await model.Tag.find_one(model.Tag.name == tag_name):
            modal = interactions.Modal(
                title="Edit tag",
                custom_id=f"edit_tag_{str(tag.id)}",
                components=[
                    interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="What do you want the tag to be named?",
                        value=tag_name,
                        placeholder="d.py cogs vs. i.py extensions",
                        custom_id="new_tag_name",
                        min_length=1,
                        max_length=100,
                        required=False,
                    ),
                    interactions.TextInput(
                        style=interactions.TextStyleType.PARAGRAPH,
                        label="What do you want the tag to include?",
                        value=tag.description,
                        placeholder="(Note: you can also put codeblocks in here!)",
                        custom_id="new_tag_description",
                        max_length=2000,
                    ),
                ],
            )

            await ctx.popup(modal)
            await ctx.send("Modal sent.", ephemeral=True)
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    @tag.subcommand()
    @interactions.option("The name of the option", autocomplete=True)
    async def delete(self, ctx: interactions.CommandContext, tag_name: str):
        """Deletes a tag that currently exists within the database."""
        await ctx.defer()

        log.debug("Matched for delete. Returning result...")

        if not self._check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        elif tag := await model.Tag.find_one(model.Tag.name == tag_name):
            await tag.delete()

            await ctx.send(
                f":heavy_check_mark: Tag `{tag_name}` has been successfully deleted.",
                ephemeral=True,
            )
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    @staticmethod
    def _check_role(ctx: interactions.CommandContext) -> bool:
        """Checks whether an invoker has the Helper role or not."""
        # TODO: please get rid of me when perms v2 is out. this is so dumb.
        return bool(
            str(src.const.METADATA["roles"]["Helper"])
            in [str(role) for role in ctx.author.roles]
        )

    @interactions.extension_autocomplete(command="tag", name="tag_name")
    async def __parse_tag(self, ctx: interactions.CommandContext, tag_name: str = ""):
        """Parses the current choice you're making with /tag."""
        letters: list = list(tag_name) if tag_name != "" else []
        tags = await model.Tag.find_all().to_list()
        tag_names = [t.name for t in tags]

        log.debug("Autocompleting tag query for choices...")

        if not letters:
            await ctx.populate(
                [
                    interactions.Choice(name=tag, value=tag)
                    for tag in (
                        tag_names[:24] if len(tag_names) > 25 else tag_names
                    )
                ]
            )

        else:
            choices: list = []

            focus: str = "".join(letters)

            for tag in tag_names:
                if focus.lower() in tag.lower() and len(choices) < 26:
                    choices.append(interactions.Choice(name=tag, value=tag))

            await ctx.populate(choices)

    @interactions.extension_modal(modal="new_tag")
    async def __new_tag(
        self, ctx: interactions.CommandContext, tag_name: str, description: str
    ):
        """Creates a new tag through the modal UI."""
        await ctx.defer(ephemeral=True)
        if not await model.Tag.find_one(model.Tag.name == tag_name):
            tag = model.Tag(
                name=tag_name,
                author_id=str(ctx.author.id),
                description=description,
                created_at=datetime.datetime.now(),
            )
            await tag.insert()

            await ctx.send(
                f":heavy_check_mark: `{tag_name}` now exists. In order to view it, please use `/tag view`.",
                ephemeral=True,
            )
        else:
            await ctx.send(
                f":x: Tag `{tag_name}` already exists.\n(Did you mean to use `/tag edit`?)",
                ephemeral=True,
            )

    @interactions.extension_listener(name="on_modal")
    async def _edit_tag(self, ctx: interactions.CommandContext):
        if not ctx.data.custom_id or not ctx.data.custom_id.startswith("edit_tag"):
            return

        tag_id = ctx.data.custom_id.removeprefix("edit_tag_")

        if tag := await model.Tag.get(PydanticObjectId(tag_id)):
            args = [[value.value for value in component.components][0] for component in ctx.data.components if component.components]

            tag_name = args[0]
            description = args[1]

            original_name = tag.name
            tag.name = tag_name
            tag.description = description
            tag.last_edited_at = datetime.datetime.now()
            await tag.save()

            await ctx.send(
                (
                    f":heavy_check_mark: Tag `{tag_name}` has been edited."
                    if tag_name == original_name
                    else f":heavy_check_mark: Tag `{original_name}` has been edited and re-named to `{tag_name}`."
                ),
                ephemeral=True,
            )
        else:
            await ctx.send("The original tag could not be found.", ephemeral=True)

    @interactions.extension_command(scope=METADATA["guild"])
    async def archive(self, ctx: interactions.CommandContext):
        """Archives this thread"""

        if not self._check_role(ctx):
            return await ctx.send(":x: You are not a helper.", ephemeral=True)

        await ctx.send("archiving...")
        await ctx.get_channel()
        await ctx.channel.modify(archived=True, locked=True)


def setup(bot, **kwargs):
    Tag(bot, **kwargs)
