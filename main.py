from fastapi import FastAPI, Depends
from pydantic import BaseModel
from helpers.db.dals.entry_dal import EntryDal
import helpers.helper as helper
from typing import Optional, List
from helpers.model import Link
from helpers.db.config import engine, Base
from dependencies import get_entry_dal

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


@app.post("/", response_model=Optional[List[Link]])
async def root(inp: Msg, entry_dal: EntryDal = Depends(get_entry_dal)):
    body = inp.msg
    if helper.check_if_amp(body):
        urls = helper.get_urls(body)
        links = await helper.get_urls_info(urls, entry_dal)
        if any(link.canonical for link in links) or any(link.amp_canonical for link in links):
            return [link.__dict__ for link in links]
        await entry_dal.save_entry(True, links)
    return None


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
