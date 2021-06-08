import asyncio
import datetime
import re
import typing

import discord
from discord.ext import commands


import github.GithubException
from github import Github


guild_ids = [701347683591389185]


class Git(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.git = Github("no u")

    async def get_repo(self):
        repo = await asyncio.to_thread(
            self.git.get_repo, "discord-py-slash-commands/discord-py-slash-command"
        )
        return repo

    async def get_pull(self, repo, pr_id: int):
        try:
            pr = await asyncio.to_thread(repo.get_pull, pr_id)
            return pr

        except github.UnknownObjectException:
            return None

    async def get_issue(self, repo, issue_id: int):
        try:
            pr = await asyncio.to_thread(repo.get_issue, issue_id)
            return pr

        except github.UnknownObjectException:
            return None

    def assemble_body(self, body: str, max_lines=7):
        """Cuts the body of an issue / pr to fit nicely"""
        output = []
        body = body.split("\n")
        for i in range(len(body)):
            if body[i].startswith("## Checklist"):
                body = body[:i]
                break
        code_block = False

        for i in range(len(body)):
            line = body[i].strip("\r")
            if line in ["", "\n", " "] or line.startswith("!image"):
                continue
            if line.startswith("## "):
                line = f"**{line[3:]}**"

            # try and remove code blocks
            if line.strip().startswith("```"):
                if not code_block:
                    code_block = True
                    continue
                else:
                    code_block = False
                    continue
            if not code_block:
                output.append(line)
            if len(output) == max_lines:
                # in case a code block got through, make sure its closed
                if "".join(output).count("```") % 2 != 0:
                    output.append("```")
                output.append(f"`... and {len(body) - i} more lines`")
                break

        return "\n".join(output)

    async def send_issue(self, message: discord.Message, issue):
        """Send a reply to a message with a formatted issue"""
        embed = discord.Embed(title=f"Issue #{issue.number}: {issue.title}")
        embed.url = issue.html_url
        embed.set_footer(
            text=f"{issue.user.name if issue.user.name else issue.user.login}",
            icon_url=issue.user.avatar_url,
        )

        if issue.state == "closed":
            embed.description = "🚫 Closed"
            embed.colour = discord.Color.greyple()
        if issue.state == "open":
            if issue.locked:
                embed.description = "🔒 Locked"
                embed.colour = discord.Color.orange()
            else:
                embed.description = "🟢 Open"
                embed.colour = discord.Color.green()
        embed.description += (
            f"{' - ' if len(issue.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in issue.labels)}\n"
            f"{self.assemble_body(issue.body)}"
        )

        await message.reply(embed=embed)

    async def send_pr(self, message: discord.Message, pr):
        """Send a reply to a message with a formatted pr"""
        embed = discord.Embed(title=f"PR #{pr.number}: {pr.title}")
        embed.url = pr.html_url
        embed.set_footer(
            text=f"{pr.user.name if pr.user.name else pr.user.login}", icon_url=pr.user.avatar_url
        )

        if pr.state == "closed":
            if pr.merged:
                embed.description = f"💜 Merged by {pr.merged_by.name} at {pr.merged_at.ctime()}"
                embed.colour = discord.Color.purple()
            else:
                embed.description = "🚫 Closed"
                embed.colour = discord.Color.greyple()
        if pr.state == "open":
            embed.description = "🟢 Open"
            embed.colour = discord.Color.green()
        embed.description += (
            f"{' - ' if len(pr.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in pr.labels)}\n"
            f"{self.assemble_body(pr.body, max_lines=5)}"
        )
        checklist = pr.body.split("## Checklist")[-1].strip("\r")
        checklist = re.sub("\[[^\s]]", "✅", checklist)
        checklist = checklist.replace("[ ]", "❌")
        embed.add_field(name="Checklist", value=checklist)

        await message.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if message.guild.id in guild_ids:
                in_data = message.clean_content.lower()

                if data := re.search(r"((pr|i)#\d(\d*))", in_data):
                    repo = await self.get_repo()
                    print(data.group())
                    if data.group().startswith("pr"):
                        # pull request
                        try:
                            pr = await self.get_pull(repo, int(data.group().split("pr#")[-1]))
                            print(pr)
                            if pr:
                                await self.send_pr(message, pr)
                        except github.UnknownObjectException:
                            print("No pull request with that ID")
                    else:
                        try:
                            issue = await self.get_issue(repo, int(data.group().split("i#")[-1]))
                            if issue:
                                await self.send_issue(message, issue)
                        except github.UnknownObjectException:
                            print("No issue with that ID")
        except Exception as e:
            print(e)


def setup(bot: commands.Bot):
    bot.add_cog(Git(bot))
