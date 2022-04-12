import interactions
from datetime import datetime
import re
import aiohttp


class Git(interactions.Extension):
    """An extension dedicated to linking PRs/issues."""

    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.url = "https://api.github.com/repos/interactions-py/library/issues/"
        self.headers = {"accept": "application/vnd.github.v3+json"}

    @interactions.extension_listener(name="on_message_create")
    async def on_message_create(self, message: interactions.Message):
        tags = [tag.strip("#") for tag in message.content.split() if tag.startswith("#")]
        if message.author.id == self.bot.me.id or message.author.bot or tags[0] == "" or not tags[0].isnumeric():
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + tags[0], headers=self.headers) as resp:
                response: dict = await resp.json()
                if len(response.keys()) == 2:
                    return
                created_at = round(datetime.fromisoformat(response['created_at'].replace('Z', '')).timestamp())
                merged_at = "None"
                closed_at = "None"
                if response['closed_at']:
                    closed_at = round(datetime.fromisoformat(response['closed_at'].replace('Z', '')).timestamp())
                    if "pull_request" in response.keys():
                        merged_at = response['pull_request']['merged_at'] or "None"
            body, tasks, checklist = self._create_fields(response)
            message._client = self.bot._http
            description = f"• Created: <t:{created_at}:R>\n"

            if response['state'] == "closed":
                if "pull_request" in response.keys():
                    if response['pull_request']['merged_at']:
                        description = description + f"• Merged: <t:{merged_at}:R> by {response['closed_by']['login']}"
                description = description + f"• Closed: <t:{closed_at}:R> by {response['closed_by']['login']}"

            if checklist and tasks:
                fields = [interactions.EmbedField(name="**About**",
                                                  value=body),
                          interactions.EmbedField(name="**Tasks**",
                                                  value=tasks,
                                                  inline=True),
                          interactions.EmbedField(name="**Checklist**",
                                                  value=checklist,
                                                  inline=True)]
            else:
                about = re.sub("\[[^\s]]", "✔️", "\n".join(body.split("\n")[:7]).replace("[ ]", "❌")) + "\n**...**"
                fields = [interactions.EmbedField(name="-",
                                                  value=about)]

            await message.reply(embeds=interactions.Embed(
                title=response['title'],
                url=response['html_url'],
                description=description,
                color=0x00b700,
                footer=interactions.EmbedFooter(
                    text=response["user"]["login"],
                    icon_url=response["user"]["avatar_url"]),
                fields=fields))

    def _prepare_PR(self, ls: list):
        _ = 0
        checklist = []
        tasks = []
        body = []
        while _ < len(ls):
            if "Checklist" in ls[_]:
                while _ < len(ls):
                    if "I've made this pull request" not in ls[_]:
                        checklist.append(ls[_])
                    else:
                        while _ < len(ls):
                            tasks.append(ls[_])
                            _ += 1
                    _ += 1
            if _ < len(ls):
                body.append(ls[_])
            _ += 1
        if "##" in body[0]:
            del body[0]
        if len(checklist) > 1 and "##" in checklist[0]:
            del checklist[0]
        body = "\n".join(body)
        checklist = re.sub("\[[^\s]]", "✔️", "\n".join(checklist)).replace("[ ]", "❌")
        tasks = re.sub("\[[^\s]]", "✔️", "\n".join(tasks)).replace("[ ]", "❌")
        return body, checklist, tasks

    def _prepare_issue(self, ls: list):
        _ = 0
        while _ < len(ls):
            if ls[_].startswith("##") or ls[_].startswith("###"):
                ls[_] = f"**{ls[_][3:].lstrip(' ')}**"
            _ += 1
        body = "\n".join(ls)
        tasks = None
        checklist = None
        return body, tasks, checklist

    def _create_fields(self, res: dict):
        _ = 0
        clean = re.sub(r'```([^```]*)```', string=res['body'], repl="`[CODEBLOCK]`").replace("\r", "").split("\n")
        dupe = False

        while _ < len(clean) - 1:
            if clean[_] == clean[_ + 1]:
                del clean[_]
                dupe = True
            elif dupe:
                del clean[_]
                dupe = False
            else:
                _ += 1
        for el in clean:
            if "![image]" in el:
                clean.remove(el)

        if "pull_request" in res.keys():
            return self._prepare_PR(clean)
        else:
            return self._prepare_issue(clean)

    def _pr_color(self, response: dict):
        if response["state"] == "open":
            return 0x00b700
        if "pull_request" in response.keys():
            if response["pull_request"]["merged_at"]:
                return 0x9e3eff
            return 0xc40000
        return 0xc0c0c0


def setup(bot):
    Git(bot)
