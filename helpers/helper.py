import helpers.static as static
from typing import List
from urlextract import URLExtract
from helpers.model import Link
from helpers.utils import get_url_info
import asyncio


# Check if the body contains an AMP link
def check_if_amp(body: str) -> bool:
    # Make body lowercase
    body = body.lower()
    # Detect if the body contains links
    if not any(map(body.__contains__, static.PROTOCOL_KEYWORDS)):
        return False
    # Detect if the body contains common AMP keywords
    return any(map(body.__contains__, static.AMP_KEYWORDS))


# Get all the URLs from the body
def get_urls(body: str) -> List[str]:
    # Set up an extractor to extract the URLs
    extractor = URLExtract()
    # Update the TLD list if it is older than x days
    extractor.update_when_older(7)
    # Run the extractor and remove any duplicates
    urls = extractor.find_urls(body, only_unique=True)
    return urls


# Loop through all the URLs, run get_url_info for each url, append Link instance to links
async def get_urls_info(urls: List[str], entry_dal) -> List[Link]:
    return await asyncio.gather(*[get_url_info(url, False, static.MAX_DEPTH, entry_dal=entry_dal) for url in urls])
