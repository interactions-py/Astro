# slash-bot
Bot for discord-py-slash-command Discord Server.  
It basically only have tag feature, release subscription 
(but actually just role giving) feature.  
I uploaded this for the demonstration of slash command.

## Paginator
This simple example shows how to easily create interactive, multiple page embeds that annyone can interact with.
```py
import discord
import discord_slash
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import Paginator

@slash.slash(name="command")
async def command(ctx:SlashContext)
embed1=discord.Embed(title="title")
embed2=discord.Embed(title="another title")
embed3=discord.Embed(title="yet another title")
pages=[embed1,embed2,embed3]

await Paginator(bot=bot,ctx=ctx,pages=pages,content="Hello there",prevLabel="Back",nextLabel="Forward",
        prevEmoji="♥",nextEmoji="♥",prevStyle=1,nextStyle=2,indexStyle=3,timeout=10)
```

## Requirements (just see `requirements.txt`)
Python >= 3.7 (not sure if it works for 3.6)  
discord.py >= 1.5.1  
discord-py-slash-command >= 1.1.0 
aiosqlite

## Any questions?
Visit [discord-py-slash-command Discord Server](https://discord.gg/KkgMBVuEkx).
