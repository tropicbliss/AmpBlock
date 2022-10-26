from fastapi import FastAPI
from pydantic import BaseModel
import helpers.helper as helper

description = """
AmpBlock is an API that extracts AMP links from messages and retrieves each of their canonical URLs.

Simply send a POST request to the root of this API and it will either return `null` if there are no AMP links detected or info regarding the extracted links (it mirrors the output of the official API). You'll have to try it out and see for yourselves.
"""

app = FastAPI(
    title="AmpBlock",
    description=description,
    version="0.0.1",
    contact={
        "name": "tropicbliss",
        "url": "https://www.tropicbliss.net/",
        "email": "tropicbliss@protonmail.com"
    },
    license_info={
        "name": "GNU GPL v3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0-standalone.html"
    }
)


class Msg(BaseModel):
    msg: str


@app.post("/")
async def root(inp: Msg):
    body = inp.msg
    if helper.check_if_amp(body):
        urls = helper.get_urls(body)
        links = await helper.get_urls_info(urls)
        if any(link.canonical for link in links) or any(link.amp_canonical for link in links):
            return [link.__dict__ for link in links]
    return None
