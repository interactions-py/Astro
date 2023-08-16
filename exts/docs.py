import asyncio

import aiohttp
import interactions as ipy
import lxml.etree as etree


def url_encode(url):
    """Partial URL encoder, because we don't want to encode slashes"""
    return url.replace(" ", "%20").lower()


def url_to_page_name(url):
    """Turns the URL of a guide into a human readable name"""
    url = url.strip("/").split("/")[-1]  # Get the last part of the url
    url = url.replace("%20", " ")
    return url


def trim_base(url):
    """Removes the base URL, and replaces %20 with spaces"""
    url = url.replace(
        "https://interactions-py.github.io/interactions.py/API%20Reference/API%20Reference/", ""
    )
    url = url.replace("%20", " ")
    return url


class DocsCommands(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.session: aiohttp.ClientSession = bot.session
        self.guides: list[str] = []
        self.search_index: list[dict] = []
        self.search_fields: dict[str, str] = {}
        asyncio.create_task(self.fetch_docs_data())

    async def fetch_docs_data(self):
        # Fetch the sitemap
        xml = await self.session.get(
            "https://interactions-py.github.io/interactions.py/sitemap.xml"
        )
        # parse the XML
        tree = etree.fromstring(await xml.read())
        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap = [page.text for page in tree.findall(".//sm:loc", namespaces)]
        # Filter the sitemap into subsections
        self.guides = [p for p in sitemap if "/Guides/" in p]
        self.api_ref = [p for p in sitemap if "/API%20Reference/" in p]

    @ipy.slash_command(name="docs")
    async def docs(self, ctx: ipy.SlashContext):
        ...

    @docs.subcommand("guide")
    @ipy.slash_option(
        "query",
        description="The page to search for",
        opt_type=ipy.OptionType.STRING,
        required=True,
        autocomplete=True,
    )
    async def guide(self, ctx: ipy.SlashContext, query: str):
        """Pull up a guide in the i.py docs"""
        for page in self.guides:
            if url_encode(query) in url_encode(page):
                await ctx.respond(page)
                return
        return "Not Found"

    @guide.autocomplete("query")
    async def guide_autocomplete(self, ctx: ipy.AutocompleteContext):
        await ctx.send(
            [
                url_to_page_name(page)
                for page in self.guides
                if url_encode(ctx.input_text) in url_encode(page)
            ]
        )

    @docs.subcommand("api")
    @ipy.slash_option(
        "query",
        description="The page to search for",
        opt_type=ipy.OptionType.STRING,
        required=True,
        autocomplete=True,
    )
    async def api(self, ctx: ipy.SlashContext, query: str):
        """Pull up an API Reference in the i.py docs"""
        for page in self.api_ref:
            if url_encode(query) in url_encode(page):
                await ctx.respond(page)
                return
        return "Not Found"

    @api.autocomplete("query")
    async def api_autocomplete(self, ctx: ipy.AutocompleteContext):
        await ctx.send(
            [
                trim_base(page)
                for page in self.api_ref
                if url_encode(ctx.input_text) in url_encode(page)
            ][:25]
        )
