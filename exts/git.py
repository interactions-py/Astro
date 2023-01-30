import asyncio
import re
import textwrap

import aiohttp
import githubkit
import naff
from githubkit.exception import RequestFailed
from githubkit.rest.models import Issue

from common.const import ASTRO_COLOR

GH_SNIPPET_REGEX = re.compile(
    r"github\.com/(\S+)/(\S+)/blob/([\S][^\/]+)/([\S][^#]+)#L([\d]+)(?:-L([\d]+))?"
)
TAG_REGEX = re.compile(r"(?:\s|^)#(\d{1,5})")
CODEBLOCK_REGEX = re.compile(r"```([^```]*)```")
IMAGE_REGEX = re.compile(r"!\[.+\]\(.+\)")
COMMENT_REGEX = re.compile(r"<!--(.*)-->")
EXCESS_NEW_LINE_REGEX = re.compile(r"(\n[\t\r ]*){3,}")


class Git(naff.Extension):
    """An extension dedicated to linking PRs/issues."""

    def __init__(self, bot):
        self.bot: naff.Client = bot
        self.owner = "interactions-py"
        self.repo = "interactions.py"
        self.gh_client = githubkit.GitHub()
        self.session: aiohttp.ClientSession = bot.session

    def clean_content(self, content: str) -> str:
        content = content.replace("### Pull-Request specification", "")
        content = content.replace("[ ]", "❌")
        content = content.replace("[x]", "✅")
        content = CODEBLOCK_REGEX.sub(string=content, repl="`[CODEBLOCK]`")
        content = IMAGE_REGEX.sub(string=content, repl="`[IMAGE]`")
        content = COMMENT_REGEX.sub(string=content, repl="")
        content = EXCESS_NEW_LINE_REGEX.sub(string=content, repl="\n\n")
        return content.strip()

    def get_color(self, issue: Issue):
        if issue.state == "open":
            return naff.Color(0x00B700)
        elif issue.pull_request and issue.pull_request.merged_at:
            return naff.Color(0x9E3EFF)
        return naff.Color(0xC40000)

    def create_timestamps(self, issue: Issue):
        timestamps = [f"• Created: <t:{round(issue.created_at.timestamp())}:R>"]

        if issue.state == "closed":
            if issue.pull_request and issue.pull_request.merged_at:
                timestamps.append(
                    f"• Merged: <t:{round(issue.pull_request.merged_at.timestamp())}:R> by"
                    f" {issue.closed_by.login}"
                )
            else:
                timestamps.append(
                    f"• Closed: <t:{round(issue.closed_at.timestamp())}:R> by"
                    f" {issue.closed_by.login}"
                )

        return "\n".join(timestamps)

    def prepare_issue(self, issue: Issue):
        embed = naff.Embed(
            title=issue.title,
            description=self.create_timestamps(issue),
            color=self.get_color(issue),
            url=issue.html_url,
        )
        if issue.user:
            embed.set_footer(text=issue.user.login, icon_url=issue.user.avatar_url)

        body = self.clean_content(issue.body or "No description")
        new_body = []

        # make all headers bold instead
        for line in body.split("\n"):  # purposely using \n for consistency
            if line.startswith("#"):
                # ideal format: ## title
                space_split = line.split(" ", 1)
                if len(space_split) > 1 and all(c == "#" for c in space_split[0].strip()):
                    line = f"**{space_split[1].strip()}**"
            new_body.append(line)

        if len(new_body) > 7:
            new_body = new_body[:7] + ["..."]

        embed.add_field("Description", "\n".join(new_body))
        return embed

    def prepare_pr(self, issue: Issue):
        embed = naff.Embed(
            title=issue.title,
            description=self.create_timestamps(issue),
            color=self.get_color(issue),
            url=issue.html_url,
        )
        if issue.user:
            embed.set_footer(text=issue.user.login, icon_url=issue.user.avatar_url)

        body = self.clean_content(issue.body or "No description")
        line_split = body.split("\n")  # purposely using \n for consistency

        # essentially, what we're trying to do is get each "part" of the pr
        # that's seperated by a header, or ##
        # we can't just use split since split removes the ##, and we also
        # want to handle prs that don't have any headers while knowing they
        # don't have a header
        header_split: list[str] = []
        current_part = []

        for line in line_split:
            if line.startswith("## "):
                if current_part:
                    header_split.append("\n".join(current_part).strip())
                current_part = []

            # well, this part is weird
            # basically, the old astro version had a "tasks" and a "checklist",
            # which were "Checklist" split into two parts based on the line below
            # we're trying to "trick" our future parser into thinking these are
            # legitmately two seperate parts by manupulating our current_part
            # to match up for what's expected
            elif "I've made this pull request" in line:
                if current_part:
                    current_part[0] = "## Tasks"
                    header_split.append("\n".join(current_part).strip())
                current_part = ["## Checklist"]

            current_part.append(line)

        # likely will be spares
        if current_part:
            header_split.append("\n".join(current_part).strip())

        for part in header_split:
            desc = part
            if part.startswith("## "):
                line_split = part.split("\n")
                title = line_split[0].removeprefix("## ").strip()
                desc = "\n".join(line_split[1:])
            else:
                title = "Description"

            if len(desc) > 1021:  # field limit
                desc = f"{desc[:1021].strip()}..."

            embed.add_field(title, desc, inline=title in ("Tasks", "Checklist"))

        return embed

    async def resolve_issue_num(self, message: naff.Message, issue_num: int):
        try:
            resp = await self.gh_client.rest.issues.async_get(self.owner, self.repo, issue_num)
        except RequestFailed:
            return

        issue = resp.parsed_data

        if issue.pull_request:
            embed = self.prepare_pr(issue)
        else:
            embed = self.prepare_issue(issue)

        await message.reply(embeds=embed)

    async def resolve_gh_snippet(self, message: naff.Message):
        # heavily inspired and slightly stolen from
        # https://github.com/NAFTeam/NAFB/blob/0460e8d2cada81e39909198ba3d84fa25f174e1a/scales/githubMessages.py#L203-L241
        # NAFB under MIT License, owner LordOfPolls

        results = GH_SNIPPET_REGEX.findall(message.content)

        if not results:
            return

        results = results[0]

        owner = results[0]
        repo = results[1]
        ref = results[2]
        file_path = results[3]
        extension = ".".join(file_path.split(".")[1:])

        start_line_num = int(results[4]) if len(results) > 4 and results[4] else 0
        end_line_num = int(results[5]) if len(results) > 5 and results[5] else -1

        if end_line_num != -1:
            # i dont even know
            end_line_num += 1

        if end_line_num != -1 and start_line_num > end_line_num:
            return

        if end_line_num == -1 and start_line_num > 0:
            end_line_num = start_line_num + 1

        async with self.session.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{file_path}"
        ) as resp:
            if resp.status != 200:
                return

            # weird code, but basically, we're trying to detect if the file is under
            # 1 MiB, because if it's larger, we really don't want to download all
            # of it and take memory

            # anyways, readexactly... reads exactly how many bytes are specified
            # however, if there are less bytes in the content (file) than
            # specified, it will throw an error as it couldn't read everything
            # we're abusing this by hoping it throws an error for files under
            # 1 MiB, and making it stop downloading a file if it's over 1 MiB
            # if it errors, we can get the data of the file from the partial variable
            # and continue on
            try:
                await resp.content.readexactly(1048577)  # one MiB + 1
                return
            except asyncio.IncompleteReadError as e:
                content = e.partial
            except Exception:  # we can get some random errors
                return

            try:
                file_data = content.decode(resp.get_encoding())
                if not file_data:
                    return
            except Exception:  # we can get some random errors
                return

            line_split = file_data.splitlines()
            file_data = line_split[start_line_num - 1 :]

            if end_line_num > 0:
                file_data = file_data[: end_line_num - start_line_num]

            final_text = textwrap.dedent("\n".join(file_data))

            # there's an invisible character here so that the resulting codeblock
            # doesn't fail if the code we're looking at has ` in it
            final_text = final_text.replace("`", "`​")

            if len(final_text) > 3900:
                character_count = 0
                new_final_text = []
                line_split = final_text.splitlines()

                for line in line_split:
                    character_count += len(line)
                    if character_count > 3900:
                        break

                    new_final_text.append(line)

                final_text = "\n".join(new_final_text)

            embed = naff.Embed(
                title=f"{owner}/{repo}",
                description=f"```{extension}\n{final_text.strip()}\n```",
                color=ASTRO_COLOR,
            )
            component = naff.Button(naff.ButtonStyles.DANGER, emoji="🗑️", custom_id="gh_delete")
            await message.suppress_embeds()
            await message.reply(embeds=embed, components=component)

    @naff.component_callback("gh_delete")  # type: ignore
    async def delete_gh(self, ctx: naff.ComponentContext):
        await ctx.defer(ephemeral=True)
        reply = await self.bot.cache.fetch_message(
            ctx.message.message_reference.channel_id,
            ctx.message.message_reference.message_id,
        )
        if reply:
            if ctx.author.id == reply.author.id or (
                isinstance(ctx.author, naff.Member)
                and ctx.author.has_permission(naff.Permissions.MANAGE_MESSAGES)
            ):
                await ctx.message.delete()
                await ctx.send("Deleted.", ephemeral=True)
            else:
                raise naff.errors.BadArgument("You do not have permission to delete this.")
        else:
            raise naff.errors.BadArgument("Could not find original message.")

    @naff.listen("message_create")
    async def on_message_create(self, event: naff.events.MessageCreate):
        message = event.message

        if message.author.bot:
            return

        if "github.com/" in message.content and "#L" in message.content:
            await self.resolve_gh_snippet(message)

        elif tag := TAG_REGEX.search(message.content):
            issue_num = int(tag.group(1))
            await self.resolve_issue_num(message, issue_num)


def setup(bot):
    Git(bot)
