import asyncio
import interactions
import dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN = dotenv.get_key(".env", "token")
EXTENSIONS = ["info", "tag", "user"]

bot = interactions.Client(TOKEN, disable_sync=True)
loop = asyncio.get_event_loop()

[bot.load(f"exts.{ext}") for ext in EXTENSIONS]

async def populate():
    return {
        "roles": [
            dict().update({role["name"]: int(role["id"])})
            for role in await bot._http.get_all_roles(789032594456576001)
        ][0],
        "channels": {
            "information": 789033206769778728,
            "helpers": 820672900583522335,
            "action-logs": 789041087149899796,
            "mod-logs": 808734093754892358
        }
    }

METADATA = loop.run_until_complete(populate())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name}.")


@bot.command(
    name="subscribe",
    description="Adds the changelog pings role, \"subscribing\" to you to release news."
)
async def subscribe(ctx: interactions.CommandContext):
    role: int = METADATA["roles"].get("Changelog pings")
    
    if role in ctx.member.roles:
        await ctx.member.remove_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role removed.", ephemeral=True)
    else:
        await ctx.member.add_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role added.", ephemeral=True)


@bot.component("language_role")
async def language_role_selection(ctx: interactions.ComponentContext):
    role: int
    
    match ctx.data.values[0]:
        case "KR":
            role = METADATA["roles"].get("한국어")
        case "RU":
            role = METADATA["roles"].get("Русский")
        case "GB":
            role = METADATA["roles"].get("Deutsch")
        case "FR":
            role = METADATA["roles"].get("Français")
        case "HI":
            role = METADATA["roles"].get("हिंदी")
        case "IT":
            role = METADATA["roles"].get("Italiano")
        case "PL":
            role = METADATA["roles"].get("Polskie")
        case "ES":
            role = METADATA["roles"].get("Español")
        case _:
            await ctx.send(":x: The role you selected was invalid.", ephemeral=True)
            return

    if role in ctx.member.roles:
        await ctx.member.remove_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role removed.", ephemeral=True)
    else:
        await ctx.member.add_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role added.", ephemeral=True)

bot.start()
