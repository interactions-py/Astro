import dotenv
import interactions
import os
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN = dotenv.get_key("../.env", "token")
EXTENSIONS = [file.replace(".py", "") for file in os.listdir("exts") if not file.startswith("_")]

bot = interactions.Client(
    TOKEN,
    disable_sync=True,
    presence=interactions.ClientPresence(
        activities=[
            interactions.PresenceActivity(name="you. 👀", type=interactions.PresenceActivityType.WATCHING),
        ],
        status=interactions.StatusType.IDLE,
    ),
)

[bot.load(f"exts.{ext}") for ext in EXTENSIONS]

def populate():
    global METADATA
    METADATA = {
        "roles": {
            "Changelog pings": 789773555792740353,
            "한국어": {"id": 791532197281529937, "emoji": "🇰🇷"},
            "Русский": {"id": 823502288726261781, "emoji": "🇷🇺"},
            "Deutsch": {"id": 853004334945796149, "emoji": "🇩🇪"},
            "Français": {"id": 876494510723588117, "emoji": "🇫🇷"},
            "हिंदी": {"id": 876854835721429023, "emoji": "🇮🇳"},
            "Italiano": {"id": 880657156213461042, "emoji": "🇮🇹"},
            "Polskie": {"id": 880657302812766209, "emoji": "🇵🇱"},
            "Español": {"id": 905859809662889994, "emoji": "🇪🇸"},
        },
        "channels": {
            "information": 789033206769778728,
            "helpers": 820672900583522335,
            "action-logs": 789041087149899796,
            "mod-logs": 808734093754892358,
        },
    }

@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name}.")


@bot.command(
    name="subscribe",
    description="Adds the changelog pings role, \"subscribing\" to you to release news.",
    scope=789032594456576001
)
async def subscribe(ctx: interactions.CommandContext):
    role: int = METADATA["roles"].get("Changelog pings")

    if role in ctx.member.roles:
        await ctx.member.remove_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role removed.", ephemeral=True)
    else:
        await ctx.member.add_role(role=role, guild_id=789032594456576001)
        await ctx.send(":heavy_check_mark: Role added.", ephemeral=True)


@bot.command(
    name="add-role-menu",
    description="N/A.",
    scope=789032594456576001
)
async def add_role_menu(ctx: interactions.CommandContext):
    if str(ctx.author.id) == "242351388137488384":
        _channel: dict = await bot._http.get_channel(790050201166675998)
        _roles: list[str] = [role for role in METADATA["roles"] if role != "Changelog pings"]
        channel = interactions.Channel(**_channel, _client=bot._http)
        role_menu = interactions.SelectMenu(
            options=[
                interactions.SelectOption(
                    label=lang,
                    value=lang,
                    emoji=interactions.Emoji(
                        id=None,
                        name=METADATA["roles"][lang]["emoji"],
                        animated=False,
                    )
                )
                for lang in _roles
            ],
            placeholder="Choose a language.",
            custom_id="language_role",
            max_values=1
        )
        await channel.send(components=role_menu)
        await ctx.send(":heavy_check_mark:", ephemeral=True)

@bot.component("language_role")
async def language_role_selection(ctx: interactions.ComponentContext, choice: str):
    role: int
    roles: dict = {}

    for _role in METADATA["roles"]:
        roles.update({_role: METADATA["roles"][_role]["emoji"]})

    match choice[0]:
        case "한국어":
            role = roles.get("한국어")
        case "Русский":
            role = roles.get("Русский")
        case "Deutsch":
            role = roles.get("Deutsch")
        case "Français":
            role = roles.get("Français")
        case "हिंदी":
            role = roles.get("हिंदी")
        case "Italiano":
            role = roles.get("Italiano")
        case "Polskie":
            role = roles.get("Polskie")
        case "Español":
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
