import datetime
import interactions
import logging
import src.const
import src.model
from interactions.ext.paginator import Page, Paginator
from src.const import *
from pymongo.database import *

log = logging.getLogger("astro.exts.tag")


class Tag(interactions.Extension):
    """An extension dedicated to /tag."""

    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.edited_name = None
        self.db: Database = kwargs.get("db")
        self.tags: Collection = self.db.Tags
        self._tags = self.tags.find({"id": TAGS_ID}).next()["tags"]

    async def get_tags(self) -> None:
        self._tags = self.tags.find({"id": TAGS_ID}).next()["tags"]

    @interactions.extension_command(scope=METADATA["guild"])
    async def tag(self, *args, **kwargs):
        ...

    @tag.subcommand()
    @interactions.option("the name of the tag", autocomplete=True)
    async def view(self, ctx: interactions.CommandContext, tag_name: str):
        """Views a tag that currently exists within the database."""
        db = self._tags

        log.debug("Matched for view. Returning result...")

        if db.get(tag_name):
            await ctx.send(db[tag_name]["description"])
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    @tag.subcommand()
    @interactions.option("The name of the tag", autocomplete=True)
    async def info(self, ctx: interactions.CommandContext, tag_name: str):
        """Gathers information about a tag that currently exists within the database."""
        db = self._tags

        log.debug("Matched for info. Returning result...")

        if db.get(tag_name):
            _author: dict = await self.bot._http.get_user(db[tag_name]["author"])
            author = interactions.User(**_author)
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
                        value=author.mention,
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="ID",
                        value=db[tag_name]["id"],
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="Timestamps",
                        value="\n".join(
                            [
                                f"Created: <t:{round(db[tag_name]['created_at'])}:R>.",
                                "Last edited: "
                                + (
                                    f"<t:{round(db[tag_name]['last_edited_at'])}:R>."
                                    if db[tag_name].get("last_edited_at")
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
        db = self._tags

        log.debug("Matched for list. Returning result...")

        _id: int = 0
        _pages: list = []
        _contents: list = []
        _embeds: list = []
        _value: str = ""

        def _divide(_list: list) -> list:
            for i in range(0, len(_list), 5):
                yield _list[i : i + 5]

        for tag in db:
            _value += f"` {_id} ` {tag}\n"
            _id += 1

        for tag_group in _divide(_value.split("\n")):
            _contents.append(tag_group)

        for content in _contents:
            new_embed = interactions.Embed(
                title="Tag list",
                description="This is the list of currently existing tags.",
                color=0x1208af,
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

    @tag.subcommand()
    @interactions.option("The name of the tag", autocomplete=True)
    async def edit(self, ctx: interactions.CommandContext, tag_name: str):
        """Edits a tag that currently exists within the database."""
        db = self._tags

        log.debug("Matched for edit. Returning result...")

        if not self._check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        elif tag_name in db:
            modal = interactions.Modal(
                title="Edit tag",
                custom_id="edit_tag",
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
                        value=db[tag_name]["description"],
                        placeholder="(Note: you can also put codeblocks in here!)",
                        custom_id="new_tag_description",
                        max_length=2000,
                    ),
                ],
            )
            self.edited_name = tag_name

            await ctx.popup(modal)
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    @tag.subcommand()
    @interactions.option("The name of the option", autocomplete=True)
    async def delete(self, ctx: interactions.CommandContext, tag_name: str):
        """Deletes a tag that currently exists within the database."""
        await ctx.defer()
        db = self._tags

        log.debug("Matched for delete. Returning result...")

        if not self._check_role(ctx):
            await ctx.send(":x: You are not a helper.", ephemeral=True)
        elif tag_name in db:
            del db[tag_name]
            self.tags.find_one_and_update({"id": TAGS_ID}, {"$set": {"tags": db}})
            await self.get_tags()

            await ctx.send(
                f":heavy_check_mark: Tag `{tag_name}` has been successfully deleted.",
                ephemeral=True,
            )
        else:
            await ctx.send(f":x: Tag `{tag_name}` does not exist.", ephemeral=True)

    def _check_role(self, ctx: interactions.CommandContext) -> bool:
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
        db = self._tags

        log.debug("Autocompleting tag query for choices...")

        if not letters:
            await ctx.populate(
                [
                    interactions.Choice(name=tag[0], value=tag[0])
                    for tag in (
                        list(db.items())[:24] if len(db) > 25 else list(db.items())
                    )
                ]
            )

        else:
            choices: list = []

            focus: str = "".join(letters)

            for tag in db:
                if focus.lower() in tag.lower() and len(choices) < 26:
                    choices.append(interactions.Choice(name=tag, value=tag))

            await ctx.populate(choices)

    @interactions.extension_modal(modal="new_tag")
    async def __new_tag(
        self, ctx: interactions.CommandContext, tag_name: str, description: str
    ):
        """Creates a new tag through the modal UI."""
        await ctx.defer(ephemeral=True)
        db = self._tags
        if tag_name not in db:
            _id = len(list(db.items())) + 1
            tag = src.model.Tag(
                id=_id,
                author=ctx.author.id,
                name=tag_name,
                description=description,
                created_at=datetime.datetime.now().timestamp(),
            )
            db.update({tag_name: tag._json})
            self.tags.find_one_and_update({"id": TAGS_ID}, {"$set": {"tags": db}})
            await self.get_tags()

            await ctx.send(
                f":heavy_check_mark: `{tag_name}` now exists. In order to view it, please use `/tag view`.",
                ephemeral=True,
            )
        else:
            await ctx.send(
                ":x: Tag `{name}` already exists.\n(Did you mean to use `/tag edit`?)",
                ephemeral=True,
            )

    @interactions.extension_modal(modal="edit_tag")
    async def __edit_tag(
        self, ctx: interactions.CommandContext, tag_name: str, description: str
    ):
        """Creates a new tag through the modal UI."""
        await ctx.defer(ephemeral=True)
        db = self._tags
        tag = src.model.Tag(
            id=db[self.edited_name]["id"],
            author=ctx.author.id,
            name=self.edited_name,
            description=description,
            created_at=db[self.edited_name]["created_at"],
            last_edited_at=datetime.datetime.now().timestamp(),
        )

        if tag_name != self.edited_name:
            del db[self.edited_name]

        db.update({tag_name: tag._json})
        self.tags.find_one_and_update({"id": TAGS_ID}, {"$set": {"tags": db}})
        await self.get_tags()

        await ctx.send(
            (
                f":heavy_check_mark: Tag `{self.edited_name}` has been edited."
                if tag_name == self.edited_name
                else f":heavy_check_mark: Tag `{self.edited_name}` has been edited and re-named to `{tag_name}`."
            ),
            ephemeral=True,
        )

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
