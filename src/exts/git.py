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
        
        try:
            if message.author.id == self.bot.me.id or message.author.bot or tags[0] == "" or not tags[0].isnumeric():
                return
        except IndexError:
            pass # i don't give a fuck. shut up python.

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + tags[0], headers=self.headers) as resp:
                response: dict = await resp.json()
                if len(response.keys()) == 2:
                    return
                print(response.keys())
            created_at, merged_at, closed_at = self._timestamps(response)
            body, tasks, checklist = self._create_fields(response)
            description = self._description(response, created_at, merged_at, closed_at)
            message._client = self.bot._http
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
                value = re.sub("\[[^\s]]", "✔️", "\n".join(body.split("\n")[:7]).replace("[ ]", "❌")) + "\n**...**"
                fields = [interactions.EmbedField(name="*Description:*", value=value)]

            await message.reply(embeds=interactions.Embed(
                title=response['title'],
                url=response['html_url'],
                description=description,
                color=self._color(response),
                footer=interactions.EmbedFooter(
                    text=response["user"]["login"],
                    icon_url=response["user"]["avatar_url"]),
                fields=fields))

    def _prepare_PR(self, clean_body: list):
        _ = 0
        checklist = []
        tasks = []
        body = []
        if len(clean_body) == 0:
            return "", "", ""
        while _ < len(clean_body):
            if "Checklist" in clean_body[_]:
                while _ < len(clean_body):
                    if "I've made this pull request" not in clean_body[_]:
                        checklist.append(clean_body[_])
                    else:
                        while _ < len(clean_body):
                            tasks.append(clean_body[_])
                            _ += 1
                    _ += 1
            if _ < len(clean_body):
                body.append(clean_body[_])
            _ += 1
        if "##" in body[0]:
            del body[0]
        if len(checklist) > 1 and "##" in checklist[0]:
            del checklist[0]
        body = "\n".join(body) or "No description"
        checklist = re.sub("\[[^\s]]", "✔️", "\n".join(checklist)).replace("[ ]", "❌")
        tasks = re.sub("\[[^\s]]", "✔️", "\n".join(tasks)).replace("[ ]", "❌")
        return body, checklist, tasks

    def _prepare_issue(self, clean_body: list):
        _ = 0
        if len(clean_body) == 0:
            return "", None, None
        while _ < len(clean_body):
            if clean_body[_].startswith("##") or clean_body[_].startswith("###"):
                clean_body[_] = f"**{clean_body[_][3:].lstrip(' ')}**"
            _ += 1
        body = "\n".join(clean_body) or "No description"
        tasks = None
        checklist = None
        return body, checklist, tasks

    def _create_fields(self, res: dict):
        _ = 0
        clean = []
        if res['body'] is not None:
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
                    clean[clean.index(el)] = "`IMAGE`"
        if "pull_request" in res.keys():
            return self._prepare_PR(clean)
        else:
            return self._prepare_issue(clean)

    def _timestamps(self, res: dict):
        created_at = round(datetime.fromisoformat(res['created_at'].replace('Z', '')).timestamp())
        merged_at = "None"
        closed_at = "None"
        if res['closed_at']:
            closed_at = round(datetime.fromisoformat(res['closed_at'].replace('Z', '')).timestamp())
            if "pull_request" in res.keys() and res['pull_request']['merged_at']:
                merged_at = round(datetime.fromisoformat(res['pull_request']['merged_at'].replace('Z', '')).timestamp())
        return created_at, merged_at, closed_at

    def _description(self, res: dict, cr_at, mrg_at, cls_at):
        description = f"• Created: <t:{cr_at}:R>\n"
        if res['state'] == "closed":
            if "pull_request" in res.keys():
                if res['pull_request']['merged_at']:
                    description += f"• Merged: <t:{mrg_at}:R> by {res['closed_by']['login']}\n"
                    return description
            description += f"• Closed: <t:{cls_at}:R> by {res['closed_by']['login']}"
        return description

    def _color(self, res: dict):
        if res["state"] == "open":
            return 0x00b700
        if "pull_request" in res.keys():
            if res["pull_request"]["merged_at"]:
                return 0x9e3eff
        return 0xc40000


def setup(bot):
    Git(bot)
