import aiohttp
import re
import interactions as ipy  # I hate the `int` suggestion lmao
from base64 import b64decode
import logging
from src.const import *
from interactions.ext.tasks import create_task, IntervalTrigger

log = logging.getLogger("astro.exts.token_check")


class DiscordTokenChecker(ipy.Extension):
    def __init__(self, bot, **kwargs):
        self.bot: ipy.Client = bot
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_GIST_API_TOKEN}",
        }
        self._token_regex = re.compile(
            r"[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,}"
        )
        self._api_url = "https://api.github.com/gists"
        self._to_delete: list[str] = []

    @create_task(IntervalTrigger(10000))
    async def delete_gist(self) -> None:
        if not self._to_delete:
            self.delete_gist.stop()
            return

        async with aiohttp.ClientSession() as session:
            gist_id = self._to_delete.pop(0)
            res = await session.request(
                "DELETE", f"{self._api_url}/{gist_id}", headers=self._headers
            )

            if res.status not in {204, 404}:
                self._to_delete.append(gist_id)  # add it back if not success

    @ipy.extension_listener(name="on_message_create")
    async def token_check(self, message: ipy.Message) -> None:
        if not message.author.bot:
            possible_tokens: list[str] = [
                token for token in self._token_regex.findall(message.content)
            ]
            tokens: list[str] = []

            for token in possible_tokens:
                try:
                    int(b64decode(token.split(".")[0] + "==", validate=True))
                except ValueError:
                    pass
                else:
                    tokens.append(token)

            if tokens:
                data = await self.post_tokens_to_gist(*tokens)
                embed = ipy.Embed(
                    title="⚠️ **Token detected** ⚠️",
                    description="The message you sent contained a discord bot token! We have posted it to a github gist"
                                ". It is not guaranteed that the token will be automatically invalidated by discord, so"
                                "if you are not notified by Discord, make sure to regenerate it!",
                )
                embed.add_field(
                    name="The link below leads to the gist with the tokens found in your message:",
                    value=f"**[TOKENS](<{data.get('html_url')}>)**",
                )
                if not self._to_delete:
                    self.delete_gist.start(self)
                self._to_delete.append(data.get("id"))
                await message.reply(embeds=embed)

    async def post_tokens_to_gist(
        self,
        *tokens: str,
    ) -> dict:
        async with aiohttp.ClientSession() as session:
            content: str = "\n".join(tokens)
            data: dict = {
                "description": "Posted Discord Bot Token(s)",
                "public": True,
                "files": {
                    "tokens.txt": {
                        "content": content,
                    },
                },
            }
            resp = await session.request(
                "POST", self._api_url, json=data, headers=self._headers
            )
            json: dict = await resp.json()
            return json


def setup(bot, **kwargs):
    DiscordTokenChecker(bot, **kwargs)
