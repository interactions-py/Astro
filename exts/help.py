import asyncio
import io

import aiohttp
import naff

import common.utils as utils
from common.const import *


class HelpChannel(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.client = bot
        self.session = aiohttp.ClientSession()
        self.help_channel: naff.GuildForum = None  # type: ignore
        asyncio.create_task(self.fill_help_channel())

    async def fill_help_channel(self):
        await self.bot.wait_until_ready()
        self.help_channel = self.bot.get_channel(METADATA["channels"]["help"])  # type: ignore

    @naff.context_menu("Create Help Thread", naff.CommandTypes.MESSAGE)  # type: ignore
    async def create_thread_context_menu(self, ctx: naff.InteractionContext):
        message: naff.Message = ctx.target  # type: ignore

        modal = naff.Modal(
            "Create Help Thread",
            [
                naff.ShortText(
                    label="What should the thread be named?",
                    value=f"[AUTO] Help thread for {message.author.username}",
                    min_length=1,
                    max_length=100,
                    custom_id="help_thread_name",
                ),
                naff.ParagraphText(
                    label="What should the question be?",
                    value=message.content,
                    min_length=1,
                    max_length=4000,
                    custom_id="edit_content",
                ),
                naff.ParagraphText(
                    label="Any addition information?",
                    required=False,
                    min_length=1,
                    max_length=1024,
                    custom_id="extra_content",
                ),
            ],
            custom_id=f"help_thread_creation_{message.channel.id}|{message.id}",
        )
        await ctx.send_modal(modal)
        await ctx.send("Modal sent.", ephemeral=True)

    def generate_tag_select(self):
        tags = self.help_channel.available_tags
        options = [
            naff.SelectOption(
                t.name,
                str(t.id),
                emoji=naff.PartialEmoji(id=t.emoji_id, name=t.emoji_name, animated=False),
            )
            for t in tags
        ]
        options.append(
            naff.SelectOption(
                label="remove all tags",
                value="remove_all_tags",
                emoji=naff.PartialEmoji.from_str("🗑"),
            ),
        )
        return naff.StringSelectMenu(
            options=options,
            placeholder="Select the tags you want",
            min_values=1,
            max_values=5,
            custom_id="tag_selection",
        )

    @naff.listen("modal_completion")
    async def context_menu_handling(self, event: naff.events.ModalCompletion):
        ctx = event.ctx

        if ctx.custom_id.startswith("help_thread_creation_"):
            await ctx.defer(ephemeral=True)

            channel_id, message_id = ctx.custom_id.removeprefix("help_thread_creation_").split("|")

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return await utils.error_send(
                    ctx, ":x: Could not find channel of message.", naff.MaterialColors.RED
                )

            message = await channel.fetch_message(int(message_id))  # type: ignore
            if not message:
                return await utils.error_send(
                    ctx, ":x: Could not fetch message.", naff.MaterialColors.RED
                )

            files: list[naff.File] = []

            if message.attachments:
                for attahcment in message.attachments:
                    if attahcment.size > 8388608:  # if it's over 8 MiB, that's a bit much
                        continue

                    async with self.session.get(attahcment.proxy_url) as resp:
                        try:
                            resp.raise_for_status()
                        except aiohttp.ClientResponseError:
                            continue

                        raw_file = await resp.read()
                        files.append(naff.File(io.BytesIO(raw_file), file_name=attahcment.filename))

            post_thread = await self.help_channel.create_post(
                ctx.responses["help_thread_name"],
                content=message.content,
                applied_tags=["996215708595794071"],
                auto_archive_duration=1440,  # type: ignore
                files=files,  # type: ignore
                reason="Auto help thread creation",
            )

            await post_thread.add_member(ctx.author)
            await post_thread.add_member(message.author)

            embed = None

            if content := ctx.responses.get("extra_content"):
                embed = naff.Embed(
                    title="Additional Information",
                    description=content,
                    color=ASTRO_COLOR,
                )
                embed.set_footer(text="Please create a thread in #help to ask questions!")

            select = self.generate_tag_select()

            original_message_button = naff.Button(
                style=naff.ButtonStyles.LINK,
                label="Original message",
                url=message.jump_url,
            )
            close_button = naff.Button(
                style=naff.ButtonStyles.DANGER,
                label="Close this thread",
                custom_id="close_thread",
            )

            actionrows = [
                naff.ActionRow(original_message_button),
                naff.ActionRow(select),
                naff.ActionRow(close_button),
            ]

            starter_message = await post_thread.send(
                "This help thread was automatically generated. Read the message above for more"
                " information.",
                embeds=embed,
                components=actionrows,
            )
            await starter_message.pin()

            await message.reply(
                f"Hey, {message.author.mention}! At this time, we only help with support-related"
                f" questions in our help channel. Please redirect to {post_thread.mention} in order"
                " to receive help."
            )
            await ctx.send(":white_check_mark: Thread created.", ephemeral=True)

    @naff.listen("thread_create")
    async def first_message_for_help(self, event: naff.events.ThreadCreate):
        thread = event.thread
        if not thread.parent_id or int(thread.parent_id) != METADATA["channels"]["help"]:
            return

        members = await thread.fetch_members()
        if any(int(m.id) == int(self.bot.user.id) for m in members):
            # an autogenerated thread, don't interfere
            return

        # idk, weird stuff, it's in the old astro code
        # make sure discord accepts the "first message" by the thread creator, see
        # https://canary.discord.com/channels/789032594456576001/850982027079319572/1039983760243961856
        await asyncio.sleep(5)

        select = self.generate_tag_select()
        close_button = naff.Button(
            style=naff.ButtonStyles.DANGER,
            label="Close this thread",
            custom_id="close_thread",
        )

        message = await thread.send(
            "Hey! Once your issue is solved, press the button below to close this thread!",
            components=[[select], [close_button]],
        )
        await message.pin()

    @naff.component_callback("close_thread")  # type: ignore
    async def close_help_thread(self, ctx: naff.ComponentContext):
        if not utils.helper_check(ctx.author) and ctx.author.id != ctx.channel.owner_id:
            return await utils.error_send(
                ctx, ":x: You are not a helper.", naff.MaterialColors.YELLOW
            )

        await ctx.send("Closing! Thank you for using our help system!")
        await ctx.channel.edit(archived=True, locked=True)


def setup(bot):
    HelpChannel(bot)
