import datetime
import importlib

import interactions as ipy
import tansy
from beanie import PydanticObjectId
from interactions.ext import paginators
from rapidfuzz import fuzz, process

import common.utils as utils
from common.const import *
from common.models import Tag


class Tags(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.client = bot

    tag = tansy.TansySlashCommand(
        name="tag",
        description="The base command for managing and viewing tags.",  # type: ignore
    )

    @tag.subcommand(
        sub_cmd_name="view",
        sub_cmd_description="Views a tag that currently exists within the database.",
    )
    async def view(
        self,
        ctx: ipy.InteractionContext,
        name: str = tansy.Option("The name of the tag to view.", autocomplete=True),
    ):
        if not (tag := await Tag.find_one(Tag.name == name)):
            raise ipy.errors.BadArgument(f"Tag {name} does not exist.")

        if len(tag.description) > 2048:
            await ctx.send(
                embed=ipy.Embed(title=tag.name, description=tag.description, color=ASTRO_COLOR)
            )
        else:
            await ctx.send(tag.description, allowed_mentions=ipy.AllowedMentions.none())

    @tag.subcommand(
        sub_cmd_name="info",
        sub_cmd_description=(
            "Gathers information about a tag that currently exists within the database."
        ),
    )
    async def info(
        self,
        ctx: ipy.InteractionContext,
        name: str = tansy.Option("The name of the tag to get.", autocomplete=True),
    ):
        tag = await Tag.find_one(Tag.name == name)
        if not tag:
            raise ipy.errors.BadArgument(f"Tag {name} does not exist.")

        embed = ipy.Embed(
            title=tag.name,
            color=ASTRO_COLOR,
        )

        embed.add_field("Author", f"<@{tag.author_id}>", inline=True)
        embed.add_field(
            "Timestamps",
            f"Created at: <t:{int(tag.created_at.timestamp())}:R>\n"
            + "Last edited:"
            f" {f'<t:{int(tag.last_edited_at.timestamp())}:R>' if tag.last_edited_at else 'N/A'}",
            inline=True,
        )
        embed.add_field(
            "Counts",
            f"Words: {len(tag.description.split())}\nCharacters: {len(tag.description)}",
            inline=True,
        )
        embed.set_footer(
            "Tags are made and maintained by the Proficient users here in the support"
            " server. Please contact one if you believe one is incorrect."
        )

        await ctx.send(embeds=embed)

    @tag.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="Lists all the tags existing in the database.",
    )
    async def list(self, ctx: ipy.InteractionContext):
        await ctx.defer()

        all_tags = await Tag.find_all().to_list()
        # generate the string summary of each tag
        tag_list = [f"` {i+1} ` {t.name}" for i, t in enumerate(all_tags)]
        # get chunks of tags, each of which have 9 tags
        # why 9? each tag, with  its name and number, can be at max
        # around ~106-107 characters (100 for name of tag, 6-7 for other parts),
        # and fields have a 1024 character limit
        # 1024 // 107 gives 9, so here we are
        chunks = [tag_list[x : x + 9] for x in range(0, len(tag_list), 9)]
        # finally, make embeds for each chunk of tags
        embeds = [
            ipy.Embed(
                title="Tag List",
                description="This is the list of currently existing tags.",
                color=ASTRO_COLOR,
                fields=[ipy.EmbedField(name="Names", value="\n".join(c))],
            )
            for c in chunks
        ]

        if len(embeds) == 1:
            await ctx.send(embeds=embeds)
            return

        pag = paginators.Paginator.create_from_embeds(self.bot, *embeds, timeout=300)
        pag.show_select_menu = True
        await pag.send(ctx)

    @tag.subcommand(
        sub_cmd_name="create",
        sub_cmd_description="Creates a tag and adds it into the database.",
    )
    @utils.proficient_only()
    async def create(self, ctx: ipy.SlashContext):
        create_modal = ipy.Modal(
            ipy.ShortText(
                label="What do you want the tag to be named?",
                placeholder="d.py cogs vs. i.py extensions",
                custom_id="tag_name",
                min_length=1,
                max_length=100,
            ),
            ipy.ParagraphText(
                label="What do you want the tag to include?",
                placeholder="(Note: you can also put codeblocks in here!)",
                custom_id="tag_description",
                min_length=1,
                max_length=4096,
            ),
            title="Create new tag",
            custom_id="astro_new_tag",
        )

        await ctx.send_modal(create_modal)
        await ctx.send(":white_check_mark: Modal sent.", ephemeral=True)

    @tag.subcommand(
        sub_cmd_name="edit",
        sub_cmd_description="Edits a tag that currently exists within the database.",
    )
    @utils.proficient_only()
    async def edit(
        self,
        ctx: ipy.SlashContext,
        name: str = tansy.Option("The name of the tag to edit.", autocomplete=True),
    ):
        tag = await Tag.find_one(Tag.name == name)
        if not tag:
            raise ipy.errors.BadArgument(f"Tag {name} does not exist.")

        edit_modal = ipy.Modal(
            ipy.ShortText(
                label="What do you want the tag to be named?",
                value=tag.name,
                placeholder="d.py cogs vs. i.py extensions",
                custom_id="tag_name",
                min_length=1,
                max_length=100,
            ),
            ipy.ParagraphText(
                label="What do you want the tag to include?",
                value=tag.description,
                placeholder="(Note: you can also put codeblocks in here!)",
                custom_id="tag_description",
                min_length=1,
                max_length=4096,
            ),
            title="Edit tag",
            custom_id=f"astro_edit_tag_{str(tag.id)}",
        )
        await ctx.send_modal(edit_modal)
        await ctx.send(":white_check_mark: Modal sent.", ephemeral=True)

    async def add_tag(self, ctx: ipy.ModalContext):
        tag_name = ctx.responses["tag_name"]
        if await Tag.find_one(Tag.name == tag_name).exists():
            return await utils.error_send(
                ctx,
                (
                    f":x: Tag `{tag_name}` already exists.\n(Did you mean to use"
                    f" {self.edit.mention()}?)"
                ),
                ipy.BrandColors.YELLOW,
            )

        await Tag(
            name=tag_name,
            author_id=str(ctx.author.id),
            description=ctx.responses["tag_description"],
            created_at=datetime.datetime.now(),
        ).create()

        await ctx.send(
            (
                f":white_check_mark: `{tag_name}` now exists. In order to view it,"
                f" please use {self.view.mention()}."
            ),
            ephemeral=True,
        )

    async def edit_tag(self, ctx: ipy.ModalContext):
        tag_id = ctx.custom_id.removeprefix("astro_edit_tag_")

        if tag := await Tag.get(PydanticObjectId(tag_id)):
            tag_name = ctx.responses["tag_name"]

            original_name = tag.name
            tag.name = tag_name
            tag.description = ctx.responses["tag_description"]
            tag.last_edited_at = datetime.datetime.now()
            await tag.save()  # type: ignore

            await ctx.send(
                (
                    f":white_check_mark: Tag `{tag_name}` has been edited."
                    if tag_name == original_name
                    else (
                        f":white_check_mark: Tag `{original_name}` has been edited and"
                        f" re-named to `{tag_name}`."
                    )
                ),
                ephemeral=True,
            )
        else:
            await ctx.send(":x: The original tag could not be found.", ephemeral=True)

    @ipy.listen("modal_completion")
    async def modal_tag_handling(self, event: ipy.events.ModalCompletion):
        ctx = event.ctx

        if ctx.custom_id == "astro_new_tag":
            await self.add_tag(ctx)

        elif ctx.custom_id.startswith("astro_edit_tag"):
            await self.edit_tag(ctx)

    @tag.subcommand(
        sub_cmd_name="delete",
        sub_cmd_description="Deletes a tag that currently exists within the database.",
    )
    @utils.proficient_only()
    async def delete(
        self,
        ctx: ipy.InteractionContext,
        name: str = tansy.Option("The name of the tag to delete.", autocomplete=True),
    ):
        await ctx.defer(ephemeral=True)

        if tag := await Tag.find_one(Tag.name == name):
            await tag.delete()  # type: ignore

            await ctx.send(
                f":white_check_mark: Tag `{name}` has been successfully deleted.",
                ephemeral=True,
            )
        else:
            raise ipy.errors.BadArgument(f"Tag {name} does not exist.")

    def _process_tag(self, tag: Tag):
        return tag.lower().strip() if isinstance(tag, str) else tag.name.lower().strip()

    @view.autocomplete("name")
    @info.autocomplete("name")
    @edit.autocomplete("name")
    @delete.autocomplete("name")
    async def tag_name_autocomplete(self, ctx: ipy.AutocompleteContext):
        if name := ctx.kwargs.get("name"):
            tags = await Tag.find_all().to_list()
            options = process.extract(
                name.lower(),
                tags,
                scorer=fuzz.partial_ratio,
                processor=self._process_tag,
                limit=25,
                score_cutoff=75,
            )
            choices = [{"name": o[0].name, "value": o[0].name} for o in options]
            await ctx.send(choices)  # type: ignore
        else:
            await ctx.send(
                [{"name": tag.name, "value": tag.name} async for tag in Tag.find_all(limit=25)]
            )


def setup(bot):
    importlib.reload(utils)
    Tags(bot)
