import asyncio
import interactions
import dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN = "OTI2OTM3ODU0MzgxMjc3MjM0.YdC8Jg.2978XwJMa19_lrclv5qIOVOg6Qg" # dotenv.get_key(".env", "token")
EXTENSIONS = ["info", "mod", "tag", "user"]

bot = interactions.Client(
    TOKEN,
    disable_sync=True,
    presence=interactions.ClientPresence(
        activities=[
            interactions.PresenceActivity(name="you.", type=interactions.PresenceActivityType.WATCHING),
        ],
        status=interactions.StatusType.IDLE,
    ),
)
loop = asyncio.get_event_loop()

[bot.load(f"exts.{ext}") for ext in EXTENSIONS]

async def populate():
    global METADATA
    METADATA = {
        "roles": {
            "Changelog pings": 789773555792740353,
            "한국어": 791532197281529937,
            "Русский": 823502288726261781,
            "Deutsch": 853004334945796149,
            "Français": 876494510723588117,
            "हिंदी": 876854835721429023,
            "Italiano": 880657156213461042,
            "Polskie": 880657302812766209,
            "Español": 905859809662889994,
        },
        "channels": {
            "information": 789033206769778728,
            "helpers": 820672900583522335,
            "action-logs": 789041087149899796,
            "mod-logs": 808734093754892358,
        },
    }

loop.run_until_complete(populate())

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
    roles: dict = {}

    for _role in METADATA["roles"]:
        roles.update({_role["name"]: _role["id"]})
    
    match ctx.data.values[0]:
        case "KR":
            role = roles.get("한국어")
        case "RU":
            role = roles.get("Русский")
        case "GB":
            role = roles.get("Deutsch")
        case "FR":
            role = roles.get("Français")
        case "HI":
            role = roles.get("हिंदी")
        case "IT":
            role = roles.get("Italiano")
        case "PL":
            role = roles.get("Polskie")
        case "ES":
            role = roles.get("Español")
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
