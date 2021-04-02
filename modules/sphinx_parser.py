import aiohttp
from bs4 import BeautifulSoup


async def search_from_sphinx(url, keyword):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            text = await res.read()
    soup = BeautifulSoup(text, "html.parser")
    return [x.get("href") for x in soup.findAll("a") if keyword in str(x)]
