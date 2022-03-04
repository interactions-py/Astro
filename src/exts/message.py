import interactions
import src.const

class Message(interactions.Extension):
    """An extension dedicated to message context menus."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot

    @interactions.extension_message_command(name="Create help thread", scope=src.const.METADATA["guild"])
    async def create_help_thread(self, ctx: interactions.CommandContext):
        _guild: dict = await self.bot._http.get_guild(int(ctx.guild_id))
        guild = interactions.Guild(**_guild, _client=self.bot._http)

        # sorry EdVraz, we'll need to manually do it for now until the helper is fixed.
        _thread: dict = await self.bot._http.create_thread(
            name=f"[AUTO] Help thread for {ctx.target.author.username}.",
            channel_id=src.const.METADATA["channels"]["help"],
            thread_type=interactions.ChannelType.GUILD_PUBLIC_THREAD.value
        )
        thread = interactions.Channel(**_thread, _client=self.bot._http)

        await thread.add_member(int(ctx.author.id))
        await thread.add_member(int(ctx.target.author.id))
        await thread.send(f"This help thread has been created by {ctx.author.mention} for {ctx.target.author.mention}. Below is the question:\n```\n{ctx.target.content}\n```")
        await ctx.send(f"{ctx.target.author.mention}, please redirect to {thread.mention} at this time.")
        await ctx.send(":heavy_check_mark: Thread created.", ephemeral=True)

def setup(bot):
    Message(bot)