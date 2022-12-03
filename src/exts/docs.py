from urllib.parse import quote

import interactions
from interactions.ext.paginator import Page, Paginator

from const import METADATA


class Docs(interactions.Extension):
    def __init__(self, client: interactions.Client) -> None:
        self.client = client

    @interactions.extension_command(scope=METADATA["guild"])
    @interactions.option("query")
    async def docs_search(self, ctx: interactions.CommandContext, search: str = None):
        """Search interactions.py's documentation."""
        if search is None:
            return await ctx.send("https://interactionspy.readthedocs.io/en/latest/index.html")

        url = f"https://interactionspy.readthedocs.io/_/api/v2/search/?q={quote(search)}&project=interactionspy&version=latest&language=en"
        async with self.client._http._req._session.get(url) as resp:
            data = await resp.json()

        if data["count"] == 0:
            return await ctx.send("No results found.")

        results = []
        for i in data["results"]:
            eb = interactions.Embed(title=i["title"], url=f"{i['domain']}{i['path']}")
            for j in i["blocks"]:
                if j["type"] == "domain":
                    content = j["highlight"]["content"]
                    highlight = (
                        j["highlight"]["content"].replace("<span>", "").replace("</span>", "")
                    )

                    if j["content"].startswith(highlight):
                        content = f"... {content}"
                    if j["content"].endswith(highlight):
                        content = f"{content} ..."

                    content = (
                        content.replace("*", "\\*")
                        .replace("_", "\\_")
                        .replace("`", "\\`")
                        .replace("~", "\\~")
                        .replace("<span>", "**")
                        .replace("</span>", "**")
                    )
                    eb.add_field(name=j["name"], value=content)
            results.append(eb)

        if len(results) == 1:
            return await ctx.send(embeds=results[0])
        await Paginator(self.client, ctx, pages=[Page(embeds=i) for i in results]).run()


def setup(client):
    Docs(client)
