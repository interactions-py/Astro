import naff as interactions
import logging
from naff import listen as event

bot = interactions.Client(intents=interactions.Intents.DEFAULT, sync_interactions=False)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


@event()
async def ready():
    await bot.change_presence(
        status=interactions.Status.ONLINE,
        activity=interactions.Activity.create("you. 👀", interactions.ActivityType.WATCHING)
    )
