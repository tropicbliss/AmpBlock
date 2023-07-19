from fastapi import FastAPI
from pydantic import BaseModel
import helpers.helper as helper

description = """
AmpBlock is an API that extracts AMP links from messages and retrieves each of their canonical URLs.

## Where's the documentation of the response data?
The response data model mirrors the response data model specified in the official documentation of [AmputatorBot](https://github.com/KilledMufasa/AmputatorBot) at the time of writing.

### Example response:
```json
[
  {
    "amp_canonical": {
      "domain": "ampproject",
      "is_alt": false,
      "is_amp": true,
      "is_cached": true,
      "is_valid": true,
      "type": "CANURL",
      "url": "https://electrek-co.cdn.ampproject.org/c/s/electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/amp/?usqp=mq331AQIKAGwASCAAgM%3D",
      "url_similarity": 0.7480314960629921
    },
    "canonical": {
      "domain": "electrek",
      "is_alt": false,
      "is_amp": false,
      "is_cached": null,
      "is_valid": true,
      "type": "REL",
      "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
      "url_similarity": 0.8900523560209425
    },
    "canonicals": [
      {
        "domain": "electrek",
        "is_alt": false,
        "is_amp": false,
        "is_cached": null,
        "is_valid": true,
        "type": "REL",
        "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
        "url_similarity": 0.8900523560209425
      },
      {
        "domain": "electrek",
        "is_alt": false,
        "is_amp": false,
        "is_cached": null,
        "is_valid": true,
        "type": "REL",
        "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
        "url_similarity": 0.8900523560209425
      }
    ],
    "origin": {
      "domain": "google",
      "is_amp": true,
      "is_cached": true,
      "is_valid": true,
      "url": "https://www.google.com/amp/s/electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/amp/"
    }
  },
  {
    "amp_canonical": {
      "domain": "ampproject",
      "is_alt": false,
      "is_amp": true,
      "is_cached": true,
      "is_valid": true,
      "type": "GOOGLE_JS_REDIRECT",
      "url": "https://electrek-co.cdn.ampproject.org/c/s/electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/amp/?usqp=mq331AQIKAGwASCAAgM%3D",
      "url_similarity": 0.7480314960629921
    },
    "canonical": {
      "domain": "electrek",
      "is_alt": false,
      "is_amp": false,
      "is_cached": null,
      "is_valid": true,
      "type": "REL",
      "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
      "url_similarity": 0.8900523560209425
    },
    "canonicals": [
      {
        "domain": "electrek",
        "is_alt": false,
        "is_amp": false,
        "is_cached": null,
        "is_valid": true,
        "type": "REL",
        "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
        "url_similarity": 0.8900523560209425
      },
      {
        "domain": "electrek",
        "is_alt": false,
        "is_amp": false,
        "is_cached": null,
        "is_valid": true,
        "type": "REL",
        "url": "https://electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/",
        "url_similarity": 0.8900523560209425
      }
    ],
    "origin": {
      "domain": "google",
      "is_amp": true,
      "is_cached": true,
      "is_valid": true,
      "url": "https://www.google.com/amp/s/electrek.co/2018/06/19/tesla-model-3-assembly-line-inside-tent-elon-musk/amp/"
    }
  }
]
```

This would be the final iteration of this API. For updated code, refer to [AmputatorBot](https://github.com/KilledMufasa/AmputatorBot) which is the project in which AmpBlock is based on.
"""

app = FastAPI(
    title="AmpBlock",
    description=description,
    version="0.1.0",
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
