import interactions
import logging
import sys

sys.path.append("..")

from const import *

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger()

presence = interactions.ClientPresence(
    activities=[
        interactions.PresenceActivity(
            name="you. 👀",
            type=interactions.PresenceActivityType.WATCHING
        ),
    ],
    status=interactions.StatusType.ONLINE,
)
bot = interactions.Client(
    TOKEN,
    intents=(
        interactions.Intents.GUILDS
        | interactions.Intents.GUILD_MEMBERS
        | interactions.Intents.GUILD_BANS
        | interactions.Intents.GUILD_MESSAGES
        | interactions.Intents.DIRECT_MESSAGES # commands can work in DMs too.
        | interactions.Intents.GUILD_MESSAGE_CONTENT
        | interactions.Intents.GUILDS
    ),
    disable_sync=True
)
[bot.load(f"exts.{ext}") for ext in EXTENSIONS]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name}.")
    # await bot.change_presence(presence)

@bot.command(
    name="subscribe",
    description="Adds the changelog pings role, \"subscribing\" to you to release news.",
    scope=METADATA["guild"]
)
async def subscribe(ctx: interactions.CommandContext):
    role: int = METADATA["roles"].get("Changelog pings")

    if role in ctx.member.roles:
        await ctx.member.remove_role(role=role, guild_id=METADATA["guild"])
        await ctx.send(":heavy_check_mark: Role removed.", ephemeral=True)
    else:
        await ctx.member.add_role(role=role, guild_id=METADATA["guild"])
        await ctx.send(":heavy_check_mark: Role added.", ephemeral=True)


@bot.command(
    name="add-role-menu",
    description="N/A.",
    scope=METADATA["guild"]
)
async def add_role_menu(ctx: interactions.CommandContext):
    if str(ctx.author.id) == "242351388137488384":
        _channel: dict = await bot._http.get_channel(METADATA["channels"]["information"])
        _roles: list[str] = [
            role for role in METADATA["roles"]
            if role != "Changelog pings"
            and role != "Helper"
            and role != "Moderator"
        ]
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
    [
        roles.update({role: METADATA["roles"][role]})
        for role in METADATA["roles"]
        if role != "Changelog pings"
        and role != "Helper"
        and role != "Moderator"
    ]

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
        case "Україна":
            role = roles.get("Україна")
        case _:
            await ctx.send(":x: The role you selected was invalid.", ephemeral=True)
            return

    if role["id"] in ctx.member.roles:
        await ctx.member.remove_role(role=role["id"], guild_id=METADATA["guild"])
        await ctx.send(":heavy_check_mark: Role removed.", ephemeral=True)
    else:
        await ctx.member.add_role(role=role["id"], guild_id=METADATA["guild"])
        await ctx.send(":heavy_check_mark: Role added.", ephemeral=True)

bot.start()
