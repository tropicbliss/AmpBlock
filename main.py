from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Msg(BaseModel):
    urls: list[str]


@app.post("/")
async def root(inp: Msg):
    return {"message": inp.urls[0]}
