import datetime
import interactions
import json
import logging
import src.const
import src.model

log = logging.getLogger("astro.exts.tag")

class Tag(interactions.Extension):
    """An extension dedicated to /tag."""

    def __init__(self, bot):
        self.bot = bot
        self.edited_name = None

    @interactions.extension_command(
        name="tag",
        description="Handles \"tags\" aka. pre-written feeds for help.",
        scope=src.const.METADATA["guild"],
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
                name="info",
                description="Gathers information about a tag.",
                options=[
                    interactions.Option(
                        type=interactions.OptionType.STRING,
                        name="name",
                        description="The name of the tag you wish to gather information on.",
                        required=True,
                        autocomplete=True,
                    )
                ]
            ),
            interactions.Option(
                type=interactions.OptionType.SUB_COMMAND,
                name="list",
                description="Lists all existing tags.",
                options=[],
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

        match ctx.data.options[0].name:
            case "view":
                await self._view_tag(ctx, name)
            case "info":
                await self._info_tag(ctx, name)
            case "list":
                await self._list_tag(ctx)
            case "create":
                await self._create_tag(ctx)
            case "edit":
                await self._edit_tag(ctx, name)
            case "delete":
                await self._delete_tag(ctx, name)

    async def _view_tag(self, ctx: interactions.CommandContext, name: str):
        """Views a tag that currently exists within the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for view. Returning result...")

        if db.get(name):
            await ctx.send(db[name]["description"])
        else:
            await ctx.send(f":x: Tag `{name}` does not exist.", ephemeral=True)

    async def _info_tag(self, ctx: interactions.CommandContext, name: str):
        """Gathers information about a tag that currently exists within the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for info. Returning result...")

        if db.get(name):
            _author: dict = await self.bot._http.get_user(db[name]["author"])
            author = interactions.User(**_author)
            embed = interactions.Embed(
                title="\"" + name + "\"" if "\"" not in name else name,
                color=0x5865F2,
                footer=interactions.EmbedFooter(text=" ".join([
                    "Tags are made and maintained by the Helpers here in the support server.",
                    "Please contact one if you believe one is incorrect."
                ])),
                fields=[
                    interactions.EmbedField(
                        name="Author",
                        value=author.mention,
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="ID",
                        value=db[name]["id"],
                        inline=True,
                    ),
                    interactions.EmbedField(
                        name="Timestamps",
                        value="\n".join([
                            f"Created: <t:{round(db[name]['created_at'])}:R>.",
                            "Last edited: " + (
                                f"<t:{round(db[name]['last_edited_at'])}:R>."
                                if db[name]["last_edited_at"]
                                else "N/A"
                            )
                        ]),
                        inline=True
                    ),
                    interactions.EmbedField(name="Content", value="Please use `/tag view`."),
                ],
            )
            await ctx.send(embeds=embed)

    async def _list_tag(self, ctx: interactions.CommandContext):
        """Lists all the tags existing in the database."""
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Matched for list. Returning result...")

        paginator = interactions.ActionRow(
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="<",
                    custom_id="list_navigate_left",
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label=">",
                    custom_id="list_navigate_right",
                ),
            ]
        )
        embed = interactions.Embed(
            title="Tags list",
            description="This is the current list of existing tags.",
            color=0x5865F2,
            fields=[
                interactions.EmbedField(
                    name="Names",
                    value=" ",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="(cont.)",
                    value=" ",
                    inline=True,
                ),
            ],
        )
        _last_name: str = ""
        cc: int = 0
        while len(embed._json["fields"][0]["value"]) < 900:
            if len(embed._json["fields"][0]["value"]) > 900:
                embed._json["fields"][1]["value"] = f"{_last_name}\n"
                break
            else:
                for name in db:
                    embed._json["fields"][0]["value"] = (
                        embed._json["fields"][0]["value"] +
                        f"` {cc} `" + (
                            "\"" + name + "\"" if "\"" not in name else name
                        ) + "\n"
                    )
                    _last_name = name
                    cc += 1
        inc: int = 0
        if len(embed._json["fields"]) > 1:
            remain_items = list(db.items())
            for item in remain_items:
                if item[0] == _last_name:
                    cutoff = remain_items[inc:]
                    while len(embed._json["fields"][1]["value"]) < 900:
                        if len(embed._json["fields"][1]["value"]) > 900:
                            break
                        else:
                            for missing in cutoff:
                                embed._json["fields"][1]["value"] = (
                                    embed._json["fields"][1]["value"] +
                                    f"` {missing[1]['id']} `" + (
                                        "\"" + missing[0] + "\"" if "\"" not in missing[0] else missing[0]
                                    ) + "\n"
                                )
                else:
                    inc += 1

        await ctx.send(embeds=embed, components=paginator)

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
                        max_length=2000,
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
                            value=db[name]["description"],
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
                db = open("./db/tags.json", "w").write(json.dumps(db, indent=4, sort_keys=True))

                await ctx.send(
                    f":heavy_check_mark: Tag `{name}` has been successfully deleted.",
                    ephemeral=True
                )
            else:
                await ctx.send(f":x: Tag `{name}` does not exist.", ephemeral=True)

    def __check_role(self, ctx: interactions.CommandContext) -> bool:
        """Checks whether an invoker has the Helper role or not."""
        # TODO: please get rid of me when perms v2 is out. this is so dumb.
        return bool(str(src.const.METADATA["roles"]["Helper"]) in [str(role) for role in ctx.author.roles])

    @interactions.extension_autocomplete(command=950227663245688862, name="name")
    async def __parse_tag(self, ctx: interactions.CommandContext, name: str=""):
        """Parses the current choice you're making with /tag."""
        letters: list = list(name) if name != "" else []
        db = json.loads(open("./db/tags.json", "r").read())

        log.debug("Autocompleting tag query for choices...")

        if not letters:
            await ctx.populate([interactions.Choice(name=tag[0], value=tag[0]) for tag in (
                list(db.items())[0:24] if len(db) > 25 else list(db.items())
            )])
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
            id = len(list(db.items())) + 1
            tag = src.model.Tag(
                id=id,
                author=ctx.author.id,
                name=name,
                description=description,
                created_at=datetime.datetime.now().timestamp()
            )
            db.update({name: tag._json})
            db = open("./db/tags.json", "w").write(json.dumps(db, indent=4, sort_keys=True))

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
        tag = src.model.Tag(
            id=db[self.edited_name]["id"],
            author=ctx.author.id,
            name=self.edited_name,
            description=description,
            created_at=db[self.edited_name]["created_at"],
            last_edited_at=datetime.datetime.now().timestamp()
        )
        db.update({self.edited_name: tag._json})
        db = open("./db/tags.json", "w").write(json.dumps(db, indent=4, sort_keys=True))

        await ctx.send(
            f":heavy_check_mark: Tag `{self.edited_name}` has been edited.",
            ephemeral=True
        )

def setup(bot):
    Tag(bot)