from helpers.model import Link
import helpers.static as static
from helpers.model import UrlMeta, CanonicalType, Canonical, Page
import validators
from validators import ValidationFailure
import tldextract
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from random import choice
from urllib.parse import urlparse
import re
from newspaper import ArticleException, Article
from difflib import SequenceMatcher
import aiohttp
from helpers.database import get_entry_by_original_url


# Get and save all the info on the URLs as a Link instance
async def get_url_info(url, use_gac, max_depth) -> Link:
    link = Link(canonicals=[])
    origin = UrlMeta(url=remove_markdown(url))
    origin.is_valid = check_if_valid_url(origin.url)
    from helpers.helper import check_if_amp
    origin.is_amp = check_if_amp(origin.url) and not any(
        map(origin.url.__contains__, static.DENYLISTED_DOMAINS))
    if origin.is_valid:
        if origin.is_amp:
            origin.is_cached = check_if_cached(origin.url)
            origin.domain = tldextract.extract(origin.url).domain
            link.origin = origin
            link = await get_canonicals(
                link=link,
                max_depth=max_depth,
                use_gac=use_gac
            )
    return link


# Remove markdown and other artifacts from the URL
def remove_markdown(url) -> str:
    markdown_chars = ("?", "(", ")", "[", "]", "\\", ",", ".", "\"", "”",
                      "`", "^", "*", "|", ">", "<", "{", "}", "~", ":", ";")
    while url.endswith(markdown_chars):
        for char in markdown_chars:
            if url.endswith(char):
                url = url[:-len(char)]
    return url


# Check if URL is valid
def check_if_valid_url(url) -> bool:
    try:
        return validators.url(url)
    except (ValidationFailure, Exception):
        return False


# Check if the page is hosted by Google, Ampproject or Bing
def check_if_cached(url) -> bool:
    # Make string lowercase
    url = url.lower()
    # Check if the page is hosted by Google, Ampproject or Bing
    return ("/amp/" in url and "www.google." in url) or ("ampproject.net" in url or "ampproject.org" in url) or \
           ("/amp/" in url and "www.bing." in url)


# Get the canonical of the URL
async def get_canonicals(link: Link, max_depth=static.MAX_DEPTH, use_db=True, use_gac=True, use_mr=True) -> Link:
    next_url = link.origin.url
    depth = 0
    while depth < max_depth:
        # Get the HTML content of the URL
        response = await get_page(next_url)
        if not response:
            return link
        # Try every soup method
        for method in CanonicalType:
            # Create a new canonical instance of the specified method
            canonical = Canonical(type=method)
            # Assign the found url and note if it is still amp
            canonical = await get_canonical_with_soup(
                r=response,
                url=next_url,
                meta=canonical,
                original_url=link.origin.url,
                use_db=use_db,
                use_gac=use_gac,
                use_mr=use_mr,
            )
            if canonical and canonical.is_valid:
                link.canonicals.append(canonical)
                # Disable resource-heavy and untrustworthy methods if a canonical without AMP was found
                if not canonical.is_amp:
                    use_gac = False
                    use_mr = False
        # Return 'empty' link if no canonicals were found
        if len(link.canonicals) == 0:
            return link
        # Sort the canonicals based on their url similarity score
        link.canonicals.sort(key=lambda c: c.url_similarity, reverse=True)
        # Filter out the canonicals that are still amp
        canonicals_solved = [c for c in link.canonicals if c.is_amp is False]
        # If there are one or more solved canonicals, pick the best one and assign it to the canonical attribute
        if len(canonicals_solved) > 0:
            link.canonical = canonicals_solved[0]
            # Assign alternative canonicals if solved canonicals have different domains
            if len(canonicals_solved) > 1:
                c_alt: Canonical = next(
                    (c for c in canonicals_solved if c.domain != link.canonical.domain), None)
                if c_alt is not None:
                    for c in link.canonicals:
                        if c.domain == c_alt.domain and c.url_similarity == c_alt.url_similarity:
                            c.is_alt = True
            return link
        # If there a no solved canonicals, return no canonical, the amp canonical or run again
        else:
            # If the found URL is the same as the one before, return no canonical or the amp canonical
            if next_url == link.canonicals[0].url:
                if len(link.canonicals) > 0:
                    amp_canonical = link.canonicals[0]
                    if link.origin.is_cached:
                        link.amp_canonical = amp_canonical
                return link
            # If the found URL is different from before, but still amp, run again with the found URL
            else:
                next_url = link.canonicals[0].url
        depth += 1
    # If there are no solved canonicals and depth has maxed out, return the amp canonical or no canonical
    if len([c for c in link.canonicals if c.is_amp is False]) == 0:
        if len(link.canonicals) > 0:
            amp_canonical = link.canonicals[0]
            if link.origin.is_cached:
                link.amp_canonical = amp_canonical
    return link


# Make a request to the page with randomized headers, make a soup, save the current url, page title and status code
async def get_page(url) -> Optional[Page]:
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=get_randomized_headers()) as session:
            async with session.get(url) as response:
                html = await response.text()
                # Make the received data searchable
                soup = BeautifulSoup(html, features="html.parser")
                title = soup.title.string if soup.title and soup.title.string else "Error: Title not found"
                page = Page(str(response.url), response.status, title, soup)
                return page
    # If the submitted page couldn't be fetched, throw an exception
    except:
        return None


# Get randomized user agent, set default accept and request English page
# This is done to prevent 403 errors.
def get_randomized_headers() -> Dict[str, str]:
    return {
        'User-Agent': choice(static.HEADERS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US'
    }


# Try to find the canonical url by scanning for the specified tag
async def get_canonical_with_soup(r, url, meta: Canonical, original_url, use_db=False,
                                  use_gac=False, use_mr=False) -> Optional[Canonical]:
    can_urls = None
    # Find canonical urls with method rel
    if meta.type == CanonicalType.REL:
        can_urls = get_can_urls_by_tags(
            r.soup.find_all(rel='canonical'), 'href', url=url)
    # Find canonical urls with method amp-canurl
    elif meta.type == CanonicalType.CANURL:
        can_urls = get_can_urls_by_tags(
            r.soup.find_all(a='amp-canurl'), 'href', url=url)
    # Find canonical urls with method og_url
    elif meta.type == CanonicalType.OG_URL:
        can_urls = get_can_urls_by_tags(r.soup.find_all(
            'meta', property='og:url'), 'content', url=url)
    # Find canonical urls with method google manual_redirect
    elif meta.type == CanonicalType.GOOGLE_MANUAL_REDIRECT:
        if 'url?q=' in r.current_url and 'www.google.' in r.current_url:
            can_urls = get_can_urls_by_tags(
                r.soup.find_all('a'), 'href', url=url)
    # Find canonical urls with method google js redirect_url
    elif meta.type == CanonicalType.GOOGLE_JS_REDIRECT:
        if 'url?' in r.current_url and 'www.google.' in r.current_url:
            js_redirect_url = get_can_url_with_regex(r.soup, re.compile(
                "var\\s?redirectUrl\\s?=\\s?([\'|\"])(.*?)\\1"))
            if js_redirect_url:
                can_urls = [js_redirect_url]
    # Find canonical urls with method bing cururl
    elif meta.type == CanonicalType.BING_ORIGINAL_URL:
        if '/amp/s/' in r.current_url and 'www.bing.' in r.current_url:
            cururl = get_can_url_with_regex(r.soup, re.compile(
                "([\'|\"])originalUrl\\1\\s?:\\s?\\1(.*?)\\1"))
            if cururl:
                can_urls = [cururl]
    # Find canonical urls with method schema_mainentity
    elif meta.type == CanonicalType.SCHEMA_MAINENTITY:
        main_entity = get_can_url_with_regex(r.soup, re.compile(
            "\"mainEntityOfPage\"\\s?:\\s?([\'|\"])(.*?)\\1"))
        if main_entity:
            can_urls = [main_entity]
    # Find canonical urls with method page tco_pagetitle
    elif meta.type == CanonicalType.TCO_PAGETITLE:
        if 'https://t.co' in r.current_url and 'amp=1' in r.current_url:
            pagetitle = r.title
            if pagetitle:
                can_urls = [pagetitle]
    # Find canonical urls with method meta http-equiv redirect
    elif meta.type == CanonicalType.META_REDIRECT:
        if use_mr:
            can_urls = get_can_urls_with_meta_redirect(
                r.soup.find_all('meta'), url=url)
    # Find canonical urls by 'guessing' a canonical link and checking the article content for similarity
    elif meta.type == CanonicalType.GUESS_AND_CHECK:
        if use_gac:
            guessed_and_checked_url = await get_can_url_with_guess_and_check(url)
            if guessed_and_checked_url:
                can_urls = [guessed_and_checked_url]
    # Find canonical urls by checking the database
    elif meta.type == CanonicalType.DATABASE:
        if use_db:
            entry = await get_entry_by_original_url(url)
            if entry and entry.canonical_url:
                can_urls = [entry.canonical_url]
    # Catch unknown canonical methods
    else:
        return None
    if can_urls:
        # Loop through every can_url found
        for can_url in can_urls:
            # If the canonical is the same as before, it's a false positive
            if can_url != url:
                # Return the canonical and if it is still AMP or not
                meta.is_valid = check_if_valid_url(url)
                if meta.is_valid:
                    meta.url = can_url
                    meta.url_similarity = SequenceMatcher(
                        None, meta.url, original_url).ratio()
                    meta.domain = tldextract.extract(meta.url).domain
                    from helpers.helper import check_if_amp
                    meta.is_amp = check_if_amp(meta.url)
                    if meta.is_amp:
                        meta.is_cached = check_if_cached(meta.url)
                    return meta
    return None


def get_can_urls_by_tags(tags, target_value, url=None) -> List[str]:
    can_values = []
    for can_tag in tags:
        value = can_tag.get(target_value)
        if value.startswith("//"):
            parsed_uri = urlparse(url)
            value = f"{parsed_uri.scheme}:{value}"
        elif value.startswith("/"):
            parsed_uri = urlparse(url)
            value = f"{parsed_uri.scheme}://{parsed_uri.netloc}{value}"
        can_values.append(value)
    return can_values


def get_can_url_with_regex(soup, regex) -> Optional[str]:
    scripts = soup.find_all("script", {"src": False})
    if scripts:
        for script in scripts:
            if script.string is not None:
                result = regex.search(script.string)
                if result:
                    url = result.group(2)
                    url = re.sub('\\\/', '/', url)
                    return url
    return None


def get_can_urls_with_meta_redirect(tags, url=None) -> List[str]:
    can_values = []
    for can_tag in tags:
        if can_tag.get('http-equiv') != 'refresh':
            continue
        if 'content' not in can_tag.attrs:
            continue
        value = can_tag.get('content')
        if "url=" not in value:
            continue
        value = value.partition("url=")[2]
        if value.startswith("//"):
            parsed_uri = urlparse(url)
            value = f"{parsed_uri.scheme}:{value}"
        elif value.startswith("/"):
            parsed_uri = urlparse(url)
            value = f"{parsed_uri.scheme}://{parsed_uri.netloc}{value}"
        can_values.append(value)
    return can_values


async def get_can_url_with_guess_and_check(url) -> Optional[str]:
    for keyword in static.AMP_KEYWORDS:
        if keyword in url:
            guessed_url = url.replace(keyword, "")
            if check_if_valid_url(guessed_url):
                guessed_page = await get_page(guessed_url)
                if guessed_page and guessed_page.status_code == 200:
                    article_similarity = get_article_similarity(
                        url, guessed_url)
                    if article_similarity > 0.6:
                        return guessed_url
                    elif article_similarity > 0.35:
                        found_urls = get_can_urls_by_tags(
                            guessed_page.soup.find_all(rel='amphtml'), 'href', url=url)
                        if found_urls and found_urls[0] == url:
                            return guessed_url
    return None


# Check how similar the article text is
def get_article_similarity(url1, url2) -> Optional[float]:
    try:
        # Download and parse first article
        article1 = Article(url1, browser_user_agent=choice(static.HEADERS))
        article1.download()
        article1.parse()
        article1_text = article1.text
        # Download and parse second article
        article2 = Article(url2, browser_user_agent=choice(static.HEADERS))
        article2.download()
        article2.parse()
        article2_text = article2.text
        # Compare the two articles and return the ratio (0-1)
        return SequenceMatcher(None, article1_text, article2_text).ratio()
    except (ArticleException, Exception):
        return None
