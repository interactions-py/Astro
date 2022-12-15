import re

import githubkit
import naff
from githubkit.exception import RequestFailed
from githubkit.rest.models import Issue

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

    def clean_content(self, content: str) -> str:
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

    @naff.listen("message_create")
    async def on_message_create(self, event: naff.events.MessageCreate):
        message = event.message

        if message.author.bot:
            return

        tag = TAG_REGEX.search(message.content)
        if not tag:
            return

        issue_num = int(tag.group(1))

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


def setup(bot):
    Git(bot)
