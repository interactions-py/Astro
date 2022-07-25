import interactions
import src.const


class Message(interactions.Extension):
    """An extension dedicated to message context menus."""

    def __init__(self, bot: interactions.Client, **kwargs):
        self.bot = bot
        self.targets: dict = {}
        self.default_tag = "996215708595794071"

    @interactions.extension_message_command(
        name="Create help thread", scope=src.const.METADATA["guild"]
    )
    async def create_help_thread(self, ctx: interactions.CommandContext):
        self.targets[int(ctx.author.id)] = ctx.target
        ch = await interactions.get(self.bot, interactions.Channel, object_id=src.const.METADATA["channels"]["help"])
        _tags = ch._extras["available_tags"]
        _options: list[interactions.SelectOption] = [
            interactions.SelectOption(
                label=tag["name"],
                value=tag["id"],
                emoji=interactions.Emoji(
                    name=tag["emoji_name"],
                ) if tag["emoji_name"] else None
            ) for tag in _tags
        ]

        modal = interactions.Modal(
            custom_id="help_thread_creation",
            title="Create help thread",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    custom_id="help_thread_name",
                    label="What should the thread be named?",
                    value=f"[AUTO] Help thread for {ctx.target.author.username}.",
                    required=True,
                    min_length=1,
                    max_length=100,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    custom_id="edit_content",
                    label="What should the question be?",
                    value=ctx.target.content,
                    required=True,
                    min_length=1,
                    max_length=4000,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    custom_id="extra_content",
                    label="Any additional information",
                    required=False,
                    min_length=1,
                    max_length=1024,
                ),
                interactions.SelectMenu(
                    custom_id="TAG_SELECTION",
                    placeholder="Select the tags you want - empty = core tag",
                    options=_options,
                    min_values=0,
                    max_values=len(_options),
                ),
            ],
        )
        await ctx.popup(modal)

    @interactions.extension_modal("help_thread_creation")
    async def _help_thread_modal(
        self,
        ctx: interactions.CommandContext,
        thread_name: str,
        content: str,
        extra_content: str = "",
        tags: list[str] = None,
    ):
        if not tags:
            tags = [self.default_tag]

        target: interactions.Message = self.targets.pop(int(ctx.author.id))
        # _guild: dict = await self.bot._http.get_guild(int(ctx.guild_id))
        # guild = interactions.Guild(**_guild, _client=self.bot._http)

        # sorry EdVraz, we'll need to manually do it for now until the helper is fixed.
        target._json["content"] = content
        attachments = False
        if target._json["attachments"]:
            del target._json["attachments"]
            attachments = True

        _thread: dict = await self.bot._http.create_forum_thread(
            self=self.bot._http,
            auto_archive_duration=1440,
            name=thread_name,
            channel_id=src.const.METADATA["channels"]["help"],
            applied_tags=tags,
            message_payload=target._json,
            reason="Auto help thread creation"
        )
        thread = interactions.Channel(**_thread, _client=self.bot._http)

        await thread.add_member(int(ctx.author.id))
        await thread.add_member(int(target.author.id))

        embed = None

        if extra_content:
            embed = interactions.Embed(
                title="Additional Information:",
                color=0xFEE75C,
                timestamp=target.timestamp,
                description=extra_content
            )

        # embed = interactions.Embed(
        #     title=thread_name,
        #     color=0xFEE75C,
        #     footer=interactions.EmbedFooter(
        #         text="Please create a thread in #help to ask questions!"
        #     ),
        #     timestamp=target.timestamp,
        # )
        # embed.add_field(name="Author", value=target.author.mention, inline=True)
        # embed.add_field(name="Helper", value=ctx.author.mention, inline=True)
        # content = (
        #     content.replace("@everyone", "")
        #     .replace("@here", "")
        #     .replace("<@&789032594456576001>", "")
        # )
        # if len(content) > 1024:
        #     short_content = content[:1021]
        #     _content = (
        #         f"{content[:1018]}...```"
        #         if short_content.count("```") % 2 == 1
        #         else f"{content[:1020]}...`"
        #         if short_content.count("`") % 2 == 1
        #         else f"{content[:1019]}**..."
        #         if short_content.count("**") % 2 == 1
        #         else f"{content[:1020]}*..."
        #         if short_content.count("*") % 2 == 1
        #         else f"{content[:1019]}__..."
        #         if short_content.count("__") % 2 == 1
        #         else f"{content[:1020]}_..."
        #         if short_content.count("_") % 2 == 1
        #         else f"{short_content}..."
        #     )
        # else:
        #     _content = content
        # embed.add_field(name="Question", value=_content, inline=False)
        #
        # if extra_content:
        #     embed.add_field(name="Additional information", value=extra_content, inline=False)
        # if target.attachments:
        #     embed.set_image(url=target.attachments[0].url)

        await thread.send(
            "This help thread was automatically generated. Read the message above for more information.",
            embeds=embed,
            components=interactions.Button(
                style=interactions.ButtonStyle.LINK, label="Original message", url=target.url
            ),
        )

        if attachments:
            await thread.send(
                f"Hey {target.author.mention}! We detected an attachment on your message! Due to discord being buggy, "
                f"we could not automatically transfer it to this thread. Please re-upload it here!"
            )

        await ctx.send(
            f"Hey, {target.author.mention}! At this time, we only help with support-related questions in our help channel. Please redirect to {thread.mention} in order to receive help."
        )
        await ctx.send(":white_check_mark: Thread created.", ephemeral=True)


def setup(bot, **kwargs):
    Message(bot, **kwargs)
