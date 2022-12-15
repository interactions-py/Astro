import asyncio
import typing
from urllib.parse import quote

import aiohttp
import naff
import orjson
from naff.ext import paginators


class Docs(naff.Extension):
    def __init__(self, client: naff.Client) -> None:
        self.client = client
        self.session = aiohttp.ClientSession()

    def drop(self):
        asyncio.create_task(self.session.close())
        super().drop()

    @naff.slash_command(name="docs-search")
    async def docs_search(
        self,
        ctx: naff.InteractionContext,
        query: typing.Annotated[
            typing.Optional[str], naff.slash_str_option("The query to search for", required=False)
        ] = None,
    ):
        """Search interactions.py's documentation."""
        if query is None:
            return await ctx.send("https://interactionspy.readthedocs.io/en/latest/index.html")

        await ctx.defer()

        url = f"https://interactionspy.readthedocs.io/_/api/v2/search/?q={quote(query)}&project=interactionspy&version=latest&language=en"
        async with self.session.get(url) as resp:
            data = await resp.json(loads=orjson.loads)

        if data["count"] == 0:
            return await ctx.send("No results found.")

        results: list[naff.Embed] = []
        for i in data["results"]:
            eb = naff.Embed(title=i["title"], url=f"{i['domain']}{i['path']}")
            for j in i["blocks"]:
                if j["type"] == "domain":
                    content = (
                        j["content"]
                        .replace("*", "\\*")
                        .replace("_", "\\_")
                        .replace("`", "\\`")
                        .replace("~", "\\~")
                    )
                    link = f"""\n[[Link]({i["domain"]}{i["path"]}#{j["id"]})]"""

                    if len(content) + len(link) > 1024:
                        content = f"{content[:1020 - len(link)]}..."
                    content += link

                    eb.add_field(name=j["name"], value=content)
            if eb.fields:
                results.append(eb)

        if len(results) == 1:
            return await ctx.send(embeds=results[0])

        pag = paginators.Paginator.create_from_embeds(self.client, *results, timeout=60)
        pag.show_select_menu = True
        await pag.send(ctx)


def setup(client):
    Docs(client)
