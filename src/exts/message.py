import interactions
import src.const


class Message(interactions.Extension):
    """An extension dedicated to message context menus."""

    def __init__(self, bot: interactions.Client, **kwargs):
        self.bot = bot
        self.targets: dict = {}

    @interactions.extension_message_command(
        name="Create help thread", scope=src.const.METADATA["guild"]
    )
    async def create_help_thread(self, ctx: interactions.CommandContext):
        self.targets[ctx.author.id] = ctx.target
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
    ):
        target: interactions.Message = self.targets.pop(ctx.author.id)
        # _guild: dict = await self.bot._http.get_guild(int(ctx.guild_id))
        # guild = interactions.Guild(**_guild, _client=self.bot._http)

        # sorry EdVraz, we'll need to manually do it for now until the helper is fixed.
        _thread: dict = await self.bot._http.create_thread(
            name=thread_name,
            channel_id=src.const.METADATA["channels"]["help"],
            thread_type=interactions.ChannelType.GUILD_PUBLIC_THREAD.value,
        )
        thread = interactions.Channel(**_thread, _client=self.bot._http)

        await thread.add_member(int(ctx.author.id))
        await thread.add_member(int(target.author.id))

        embed = interactions.Embed(
            title=thread_name,
            color=0xFEE75C,
            footer=interactions.EmbedFooter(
                text="Please create a thread in #help to ask questions!"
            ),
            timestamp=target.timestamp,
        )
        embed.add_field(name="Author", value=target.author.mention, inline=True)
        embed.add_field(name="Helper", value=ctx.author.mention, inline=True)
        content = (
            content.replace("@everyone", "")
            .replace("@here", "")
            .replace("<@&789032594456576001>", "")
        )
        if len(content) > 1024:
            short_content = content[:1021]
            _content = (
                f"{content[:1018]}...```"
                if short_content.count("```") % 2 == 1
                else f"{content[:1020]}...`"
                if short_content.count("`") % 2 == 1
                else f"{content[:1019]}**..."
                if short_content.count("**") % 2 == 1
                else f"{content[:1020]}*..."
                if short_content.count("*") % 2 == 1
                else f"{content[:1019]}__..."
                if short_content.count("__") % 2 == 1
                else f"{content[:1020]}_..."
                if short_content.count("_") % 2 == 1
                else f"{short_content}..."
            )
        else:
            _content = content
        embed.add_field(name="Question", value=_content, inline=False)

        if extra_content:
            embed.add_field(name="Additional information", value=extra_content, inline=False)
        if target.attachments:
            embed.set_image(url=target.attachments[0].url)

        await thread.send(
            "This help thread was automatically generated.",
            embeds=embed,
            components=interactions.Button(
                style=interactions.ButtonStyle.LINK, label="Original message", url=target.url
            ),
        )
        await ctx.send(
            f"Hey, {target.author.mention}! At this time, we only help with support-related questions in our help channel. Please redirect to {thread.mention} in order to receive help."
        )
        await ctx.send(":white_check_mark: Thread created.", ephemeral=True)


def setup(bot, **kwargs):
    Message(bot, **kwargs)
