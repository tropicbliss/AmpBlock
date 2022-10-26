from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Msg(BaseModel):
    urls: list[str]


@app.get("/")
async def hello(inp: Msg):
    return {"message": "bonjour!"}


@app.post("/")
async def root(inp: Msg):
    return {"message": inp.urls[0]}
