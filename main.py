from fastapi import FastAPI
from pydantic import BaseModel
import helpers.helper as helper

app = FastAPI()


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
