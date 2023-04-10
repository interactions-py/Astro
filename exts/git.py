import asyncio
import contextlib
import re
import textwrap

import aiohttp
import githubkit
import interactions as ipy
import unidiff
from githubkit.exception import RequestFailed
from githubkit.rest.models import Issue
from interactions.ext import paginators
from interactions.ext import prefixed_commands as prefixed

from common.const import ASTRO_COLOR

GH_SNIPPET_REGEX = re.compile(
    r"https?://github\.com/(\S+)/(\S+)/blob/([\S][^\/]+)/([\S][^#]+)#L([\d]+)(?:-L([\d]+))?"
)
GH_COMMIT_REGEX = re.compile(r"https?://github\.com/(\S+)/(\S+)/commit/([0-9a-fA-F]{,40})")
TAG_REGEX = re.compile(r"(?:\s|^)#(\d{1,5})")
CODEBLOCK_REGEX = re.compile(r"```([^```]*)```")
IMAGE_REGEX = re.compile(r"!\[.+\]\(.+\)")
COMMENT_REGEX = re.compile(r"<!--(.*)-->")
EXCESS_NEW_LINE_REGEX = re.compile(r"(\n[\t\r ]*){3,}")


class GitPaginator(paginators.Paginator):
    def create_components(self, disable: bool = False):
        actionrows = super().create_components(disable=disable)

        # basically:
        # - find the callback button (in our case, the delete button)
        # - if found, make it red and use the gh_delete custom id for it
        for actionrow in actionrows:
            for component in actionrow.components:
                if (
                    isinstance(component, ipy.Button)
                    and component.custom_id
                    and "callback" in component.custom_id
                ):
                    component.custom_id = "gh_delete"
                    component.style = ipy.ButtonStyle.DANGER

        return actionrows


class CustomStrIterator:
    def __init__(self, strs: list[str]) -> None:
        self.strs = strs
        self.index = 0
        self.length = len(self.strs)

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.index >= self.length:
            raise StopIteration

        result = self.strs[self.index]
        self.index += 1
        return result

    def next(self) -> str:
        return self.__next__()

    def back(self) -> None:
        self.index -= 1


class Git(ipy.Extension):
    """An extension dedicated to linking PRs/issues."""

    def __init__(self, bot):
        self.bot: ipy.Client = bot
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
            return ipy.Color(0x00B700)
        elif issue.pull_request and issue.pull_request.merged_at:
            return ipy.Color(0x9E3EFF)
        return ipy.Color(0xC40000)

    def create_timestamps(self, issue: Issue):
        timestamps = [f"• Created: <t:{round(issue.created_at.timestamp())}:R>"]

        if issue.state == "closed":
            if issue.pull_request and issue.pull_request.merged_at:
                timestamps.append(
                    f"• Merged: <t:{round(issue.pull_request.merged_at.timestamp())}:R>"
                    f" by {issue.closed_by.login}"
                )
            else:
                timestamps.append(
                    f"• Closed: <t:{round(issue.closed_at.timestamp())}:R> by"
                    f" {issue.closed_by.login}"
                )

        return "\n".join(timestamps)

    def prepare_issue(self, issue: Issue):
        embed = ipy.Embed(
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
        embed = ipy.Embed(
            title=issue.title,
            description=self.create_timestamps(issue),
            color=self.get_color(issue),
            url=issue.html_url,
        )
        if issue.user:
            embed.set_footer(text=issue.user.login, icon_url=issue.user.avatar_url)

        body = self.clean_content(issue.body or "No description")
        line_split = body.split("\n")  # purposely using \n for consistency
        line_iter = CustomStrIterator(line_split)  # we need to go back and forward at will

        # essentially, what we're trying to do is get each "part" of the pr
        # that's seperated by a header, or ##
        # we can't just use split since split removes the ##, and we also
        # want to handle prs that don't have any headers while knowing they
        # don't have a header
        header_split: list[str] = []
        current_part = []

        check_types = False

        for line in line_iter:
            # we need to extract the pr type so it doesnt take 200 lines
            # we also need to ignore whitespace until we get to the checkboxes, so take this
            # ugly hack
            if line.startswith("## Pull Request Type"):
                check_types = True

            # once we're ready to check the checkboxes and know we're searching for types in the first
            # place, we go in here
            elif check_types and (line.startswith("- ✅") or line.startswith("- ❌")):
                line_iter.back()  # rewind to previous line
                types: list[str] = []

                while (line := line_iter.next()) and (
                    line.startswith("- ✅") or line.startswith("- ❌")
                ):  # while the next line is still a checkbox line
                    if line.startswith("- ✅"):
                        types.append(line.removeprefix("- ✅ ").strip())

                if types:
                    embed.description = (
                        f"• Pull Request Type: {', '.join(types)}\n{embed.description}"
                    )

                check_types = False

                # continue iter until next title
                while (line := line_iter.next()) and not line.startswith("## "):
                    continue
                line_iter.back()

                continue

            elif line.startswith("## "):
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

            if not check_types:
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
                if not desc:
                    desc = "N/A"
            else:
                title = "Description"

            if len(desc) > 1021:  # field limit
                desc = f"{desc[:1021].strip()}..."

            embed.add_field(
                title,
                desc,
                inline=title in ("Python Compatibility", "Tasks", "Checklist"),
            )

        return embed

    async def resolve_issue_num(self, message: ipy.Message, issue_num: int):
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

    async def resolve_gh_snippet(self, message: ipy.Message):
        # heavily inspired and slightly stolen from
        # https://github.com/NAFTeam/NAFB/blob/0460e8d2cada81e39909198ba3d84fa25f174e1a/scales/githubMessages.py#L203-L241
        # NAFB under MIT License, owner LordOfPolls

        results = GH_SNIPPET_REGEX.search(message.content)

        if not results:
            return

        owner = results[1]
        repo = results[2]
        ref = results[3]
        file_path = results[4]
        extension = ".".join(file_path.split(".")[1:])

        start_line_num = int(results[5]) if results.end() > 3 and results[5] else 0
        end_line_num = int(results[6]) if results.end() > 4 and results[6] else -1

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

            if not final_text:
                return

            embed = ipy.Embed(
                title=f"{owner}/{repo}",
                description=f"```{extension}\n{final_text.strip()}\n```",
                color=ASTRO_COLOR,
            )
            component = ipy.Button(style=ipy.ButtonStyle.DANGER, emoji="🗑️", custom_id="gh_delete")
            await message.suppress_embeds()
            await message.reply(embeds=embed, components=component)

    async def resolve_gh_commit_diff(self, message: ipy.Message):
        results = GH_COMMIT_REGEX.search(message.content)

        if not results:
            return

        owner = results[1]
        repo = results[2]
        commit_hash = results[3]

        # get special funky url that gets us diff
        async with self.session.get(
            f"https://github.com/{owner}/{repo}/commit/{commit_hash}.diff"
        ) as resp:
            if resp.status != 200:
                return

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

        # now, the raw diff we do get is... eh. yeah, it's eh, and i don't want to display it
        # so we'll do some processing to make it not so eh
        processed_diff = unidiff.PatchSet.from_string(file_data)
        final_diff_builder: list[str] = []

        for diff in processed_diff:
            diff: unidiff.PatchedFile
            diff_text = str(diff)

            entry = f"--- {diff.path} ---"
            if diff.is_rename:
                entry = f"--- {diff.source_file[2:]} > {diff.target_file[2:]} ---"
            new_diff_builder: list[str] = [entry]

            try:
                first_double_at = diff_text.index("@@")
                rest_of_diff = diff_text[first_double_at:].strip()

                line_split = rest_of_diff.splitlines()
                if "No newline at end of file" in line_split[-1]:
                    line_split = line_split[:-1]

                if diff.is_removed_file:
                    new_diff_builder.append("File deleted.")
                elif diff.added + diff.removed > 1000:
                    # we have to draw the line somewhere
                    new_diff_builder.append("File changed. Large changes have not been rendered.")
                else:
                    new_diff_builder.append("\n".join(line_split).strip())

            except ValueError:
                # special cases - usually deletions or renames
                if diff.is_rename:
                    new_diff_builder.append("File renamed.")
                elif diff.is_removed_file:
                    new_diff_builder.append("File deleted.")
                elif diff.is_added_file:
                    new_diff_builder.append("File created.")
                else:
                    new_diff_builder.append("Binary file changed.")

            final_diff_builder.append("\n".join(new_diff_builder))

        final_diff = "\n\n".join(final_diff_builder)
        final_diff = final_diff.replace("`", "`​")

        embeds: list[ipy.Embed] = []
        current_entries: list[str] = []

        current_length = 0
        line_split = final_diff.splitlines()

        url = f"https://github.com/{owner}/{repo}/commit/{commit_hash}"
        title = f"{owner}/{repo}@{commit_hash}"

        # the gh embed that gh generates has the title of the commit
        # if we can find it, exploit it by using the title from the embed as the
        # title of our own embed
        if possible_gh_embed := next((e for e in message.embeds if e.url and e.url == url), None):
            title = possible_gh_embed.title
        else:
            with contextlib.suppress(RequestFailed):
                resp = await self.gh_client.rest.git.async_get_commit(owner, repo, commit_hash)
                data = resp.parsed_data

                # this is around what gh does for their embeds
                first_line = data.message.splitlines()[0].strip()
                with_extras = f"{first_line} · {owner}/{repo}@{data.sha[:7]}"
                title = with_extras if len(with_extras) <= 70 else f"{with_extras[:67]}..."

        for line in line_split:
            current_length += len(line)
            if current_length > 3700:
                current_text = "\n".join(current_entries).strip()
                embeds.append(
                    ipy.Embed(
                        title=title,
                        url=url,
                        description=f"```diff\n{current_text}\n```",
                        color=ASTRO_COLOR,
                    )
                )
                current_entries = []
                current_length = 0

            current_entries.append(line)

        if current_entries:
            current_text = "\n".join(current_entries).strip()
            embeds.append(
                ipy.Embed(
                    title=title,
                    url=url,
                    description=f"```diff\n{current_text}\n```",
                    color=ASTRO_COLOR,
                )
            )

        if not embeds:
            return

        if len(embeds) > 1:
            the_pag = GitPaginator.create_from_embeds(self.bot, *embeds, timeout=300)
            the_pag.show_callback_button = True
            the_pag.callback_button_emoji = "🗑️"
            the_pag.callback = self.delete_gh.callback

            fake_ctx = prefixed.PrefixedContext.from_message(self.bot, message)

            await message.suppress_embeds()
            await the_pag.reply(fake_ctx)

        else:
            component = ipy.Button(style=ipy.ButtonStyle.DANGER, emoji="🗑️", custom_id="gh_delete")
            await message.suppress_embeds()
            await message.reply(embeds=embeds, components=component)

    @ipy.component_callback("gh_delete")  # type: ignore
    async def delete_gh(self, ctx: ipy.ComponentContext):
        await ctx.defer(ephemeral=True)
        reply = await self.bot.cache.fetch_message(
            ctx.message.message_reference.channel_id,
            ctx.message.message_reference.message_id,
        )
        if reply:
            if ctx.author.id == reply.author.id or (
                isinstance(ctx.author, ipy.Member)
                and ctx.author.has_permission(ipy.Permissions.MANAGE_MESSAGES)
            ):
                await ctx.message.delete()
                await ctx.send("Deleted.", ephemeral=True)
            else:
                raise ipy.errors.BadArgument("You do not have permission to delete this.")
        else:
            raise ipy.errors.BadArgument("Could not find original message.")

    @ipy.listen("message_create")
    async def on_message_create(self, event: ipy.events.MessageCreate):
        message = event.message

        if message.author.bot:
            return

        if "github.com/" in message.content:
            if "#L" in message.content:
                await self.resolve_gh_snippet(message)
            elif "commit" in message.content:
                await self.resolve_gh_commit_diff(message)

        elif tag := TAG_REGEX.search(message.content):
            issue_num = int(tag.group(1))
            await self.resolve_issue_num(message, issue_num)


def setup(bot):
    Git(bot)
