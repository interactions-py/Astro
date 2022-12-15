import typing

import naff

from common.const import METADATA


async def check_admin(ctx: naff.Context):
    return isinstance(ctx.author, naff.Member) and ctx.author.has_permission(
        naff.Permissions.ADMINISTRATOR
    )


class Roles(naff.Extension):
    def __init__(self, bot: naff.Client):
        self.client = bot
        self.subscribe_name_map = {
            str(METADATA["roles"]["Changelog pings"]): "Changelog pings",
            str(METADATA["roles"]["External Changelog pings"]): "External Changelog pings",
        }

    @naff.slash_command(
        "subscribe",
        description='Adds the changelog and/or external pings role, "subscribing" to you to release news.',
    )
    @naff.slash_option(
        "changelog",
        "To what changelogs do you want to subscribe? (default only main library)",
        naff.OptionTypes.STRING,
        choices=[
            naff.SlashCommandChoice(
                name="Only Main Library Changelogs", value=str(METADATA["roles"]["Changelog pings"])
            ),
            naff.SlashCommandChoice(
                name="Only External Library Changelogs",
                value=str(METADATA["roles"]["External Changelog pings"]),
            ),
            naff.SlashCommandChoice(
                name="Both Changelogs",
                value=f"{METADATA['roles']['Changelog pings']} {METADATA['roles']['External Changelog pings']}",
            ),
        ],
        required=False,
    )
    async def subscribe(
        self,
        ctx: naff.InteractionContext,
        changelog: str = str(METADATA["roles"]["Changelog pings"]),
    ):
        await ctx.defer(ephemeral=True)

        if typing.TYPE_CHECKING:
            assert isinstance(ctx.author, naff.Member)

        author_roles = set(ctx.author._role_ids)  # don't want to update roles till end
        str_builder = [":heavy_check_mark:"]

        for role_id in changelog.split(" "):  # kinda smart way of fitting 2+ roles in a choice
            action_word = ""

            if ctx.author.has_role(role_id):
                author_roles.remove(int(role_id))
                action_word = "removed"
            else:
                author_roles.add(int(role_id))
                action_word = "added"

            role_name = self.subscribe_name_map[role_id]
            # this looks weird out of context, but it'll look like:
            # `Changelog pings` role added.
            # which seems pretty natural to me
            str_builder.append(f"`{role_name}` role {action_word}.")

        await ctx.author.edit(roles=author_roles)

        await ctx.send(" ".join(str_builder), ephemeral=True)

    @naff.check(check_admin)  # type: ignore - putting it first avoids a weird typehint thing
    @naff.slash_command(
        "add-role-menu",
        description="N/A.",
        default_member_permissions=naff.Permissions.ADMINISTRATOR,
    )
    async def add_role_menu(self, ctx: naff.InteractionContext):
        await ctx.defer(ephemeral=True)

        info_channel = await self.bot.fetch_channel(METADATA["channels"]["information"])

        role_menu = naff.StringSelectMenu(
            options=[
                naff.SelectOption(
                    label=lang,
                    # if it were up to me, the value would be the role id
                    # sadly, we must keep backwards compat
                    value=lang,
                    emoji=naff.PartialEmoji(
                        id=None,
                        name=role["emoji"],
                        animated=False,
                    ),
                )
                for lang, role in METADATA["language_roles"].items()
            ],
            placeholder="Choose a language.",
            custom_id="language_role",
            min_values=1,
            max_values=25,
        )

        await info_channel.send(components=role_menu)  # type: ignore
        await ctx.send(":heavy_check_mark:", ephemeral=True)

    @naff.component_callback("language_role")  # type: ignore
    async def on_astro_language_role_select(self, ctx: naff.ComponentContext):
        await ctx.defer(ephemeral=True)

        if typing.TYPE_CHECKING:
            assert isinstance(ctx.author, naff.Member)

        # same idea as subscribe, but...
        author_roles = set(ctx.author._role_ids)

        # since there are a lot more languages than roles, i wanted to make the result
        # message a bit nicer. that requires having both of these lists
        added = []
        removed = []

        for language in ctx.values:
            language: str

            role = METADATA["language_roles"].get(language)
            if not role:
                # this shouldn't happen
                return await ctx.send(":x: The role you selected was invalid.", ephemeral=True)

            if ctx.author.has_role(role["id"]):
                author_roles.remove(int(role["id"]))
                removed.append(f"`{language}`")  # thankfully, the language here is its role name
            else:
                author_roles.add(int(role["id"]))
                added.append(f"`{language}`")

        await ctx.author.edit(roles=author_roles)

        resp = ":heavy_check_mark: "
        # yep, all we're doing is listing out the roles added and removed
        if added:
            resp += f"Added: {', '.join(added)}. "
        if removed:
            resp += f"Removed: {', '.join(removed)}."
        resp = resp.strip()  # not like it's needed, but still
        await ctx.send(resp, ephemeral=True)


def setup(bot):
    Roles(bot)
