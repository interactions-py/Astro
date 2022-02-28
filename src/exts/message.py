import interactions

class Message(interactions.Extension):
    """An extension dedicated to message context menus."""

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_message_command(name="Create help thread")
    async def create_help_thread(self, ctx: interactions.CommandContext):
        thread: interactions.Channel = await ctx.guild.create_thread(
            name="[AUTO] Contextual help thread.",
            channel_id=898281873946579034
        )
        await thread.send(f"This help thread has been created by {ctx.author.mention}. Below is the question:\n```\n{ctx.target.content}\n```")
        await ctx.send(":heavy_check_mark: Thread created.", ephemeral=True)

def setup(bot):
    Message(bot)