import asyncio
import aiohttp
import interactions as ipy
import lxml.etree as etree

class DocsCommands(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.session: aiohttp.ClientSession = bot.session
        self.sitemap: list[str] = []
        self.guides: list[str] = []
        self.search_index: list[dict] = []
        self.search_fields: dict[str, str] = {}
        asyncio.create_task(self.fetch_docs_data())

    async def fetch_docs_data(self):
        namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        xml = (await self.session.get("https://interactions-py.github.io/interactions.py/sitemap.xml"))
        tree = etree.fromstring(await xml.read())
        self.sitemap = [page.text for page in tree.findall(".//sm:loc", namespaces)]
        self.guides = [p for p in self.sitemap if '/Guides/' in p]
        self.api_ref = [p for p in self.sitemap if '/API%20Reference/' in p]
        

        search = await (await self.session.get("https://interactions-py.github.io/interactions.py/search/search_index.json")).json()
        self.search_index = search['docs']
        self.search_fields = search['config']['fields']


    @ipy.slash_command(name="docs")
    @ipy.slash_option("query", "The query to search for", ipy.OptionType.STRING, required=True)
    async def docs(self, ctx: ipy.SlashContext, query: str):
        ...

    @docs.subcommand('guide')
    @ipy.slash_option("query", "The query to search for", ipy.OptionType.STRING, required=True, autocomplete=True)
    async def guide(self, ctx: ipy.SlashContext, query: str):
        """Pull up a guide in the i.py docs"""
        for page in self.guides:
            if query.lower().replace(' ', '%20') in page.lower():
                await ctx.respond(page)
                return
        return 'Not Found'
    
    @guide.autocomplete("query")
    async def guide_autocomplete(self, ctx: ipy.AutocompleteContext):
        def pretify(url):
            url = url.strip('/').split('/')[-1]  # Get the last part of the url
            url = url.replace('%20', ' ')
            return url
        await ctx.send([pretify(page) for page in self.guides if ctx.input_text.lower().replace(' ', '%20') in page.lower()])

            
    @docs.subcommand('api')
    @ipy.slash_option("query", "The query to search for", ipy.OptionType.STRING, required=True, autocomplete=True)
    async def api(self, ctx: ipy.SlashContext, query: str):
        """Pull up an API Reference in the i.py docs"""
        for page in self.api_ref:
            if query.lower().replace(' ', '%20') in page.lower():
                await ctx.respond(page)
                return

    @api.autocomplete("query")
    async def api_autocomplete(self, ctx: ipy.AutocompleteContext):
        def pretify(url):
            url = url.replace('https://interactions-py.github.io/interactions.py/API%20Reference/API%20Reference/', '')
            url = url.replace('%20', ' ')
            return url
        await ctx.send([pretify(page) for page in self.api_ref if ctx.input_text.lower().replace(' ', '%20') in page.lower()][:25])

    @docs.subcommand('search')
    @ipy.slash_option("query", "The query to search for", ipy.OptionType.STRING, required=True)
    async def search(self, ctx: ipy.SlashContext, query: str):
        """Search the i.py docs"""
        def pretify(result):
            title = result.replace('<code>', '`').replace('</code>', '`')
            return title[:ipy.EMBED_MAX_NAME_LENGTH]
        results = await self.do_search(ctx, query)
        embed = ipy.Embed(title=f"Search results for '{query}'", color=ipy.BrandColors.BLURPLE)
        for result in results[:10]:
            embed.add_field(name=pretify(result[0]['title']), value='https://interactions-py.github.io/interactions.py/' + result[0]['location'])
        await ctx.respond(embed=embed)


    async def do_search(self, ctx, query):
        results = []
        for page in self.search_index:
            for field in self.search_fields.items():
                if page.get(field[0]) is None:
                    continue
                if query.lower() in page[field[0]].lower():
                    results.append((page, field[1]['boost']))
        if len(results) == 0:
            await ctx.respond('No results found')
            return
        results.sort(key=lambda x: x[1], reverse=True)
        return results
