import helpers.static as static
from typing import List, Optional
from sqlalchemy import VARCHAR
from helpers.model import Link
import sqlalchemy
import databases
from pydantic import BaseModel


class Entry(BaseModel):
    entry_id: int
    original_url: str
    canonical_url: str


DATABASE_URL = "mysql+mysqlconnector://{username}:{password}@" \
    "{hostname}/{databasename}".format(
        username=static.DB_USERNAME,
        password=static.DB_PASSWORD,
        hostname=static.DB_HOSTNAME,
        databasename=static.DB_DATABASENAME)
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
entry = sqlalchemy.Table(
    "URLConversions",
    metadata,
    sqlalchemy.Column("entry_id", sqlalchemy.Integer,
                      primary_key=True, autoincrement=True),
    sqlalchemy.Column("original_url", sqlalchemy.VARCHAR(4000)),
    sqlalchemy.Column("canonical_url", VARCHAR(4000))
)
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


async def get_entry_by_original_url(original_url) -> Optional[Entry]:
    query = "SELECT * FROM URLConversion WHERE original_url = :original_url AND canonical_url IS NOT NULL ORDER BY entry_id DESC LIMIT 1"
    values = {"original_url": original_url}
    return await database.execute(query=query, values=values)


async def add_data(original_url=None, canonical_url=None):
    query = entry.insert().values(original_url=original_url, canonical_url=canonical_url)
    await database.execute(query)
    return


async def save_entry(save_to_database, links: List[Link]):
    if save_to_database:
        for link in links:
            if link.origin and link.origin.is_amp:
                await add_data(original_url=link.origin.url,
                               canonical_url=link.canonical.url if link.canonical else None)
    return
