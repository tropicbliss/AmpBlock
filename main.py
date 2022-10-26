from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Msg(BaseModel):
    msg: List[str]


@app.post("/")
async def root(inp: Msg):
    return {"message": inp.msg[0]}
