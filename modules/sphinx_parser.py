import re
import aiohttp
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz


async def search_from_sphinx(url, keyword, fuzzSort=True):
    """
    Searches sphinx for a pages matching keyword
    :param url: url of sphinx docs
    :param keyword: the keyword to search for
    :param fuzzSort: should fuzzy matching/sorting be used
    :return: list of matches
    """
    keyword = keyword.lower()
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            text = await res.read()
    soup = BeautifulSoup(text, "html.parser")

    if fuzzSort:
        # utilises fuzzy string matching to determine which page is most likely to be what the user wants
        rData = {}
        data = [x.get("href") for x in soup.find_all("a") if len(x.get("href")) > 3]

        for val in data:
            # remove any links to github or sphinx, we're after docs pages here
            if re.search(r'\.org*?$', val) or val.startswith("https://github.com/"):
                continue

            # get topic of each link, while still preserving the link itself
            val = (val, re.sub(r'\.html$', '', val)
                   .split(".")[-1]
                   .replace("_", " "))

            # determine how similar this topic is to the keyword
            ratio = fuzz.ratio(val[1].lower(), keyword)
            rData[val[0]] = ratio

        # get top 5 values
        data = sorted(rData, key=rData.get, reverse=True)[:5]

    else:
        data = [x.get("href") for x in soup.findAll("a") if keyword in str(x).lower()]

    return data