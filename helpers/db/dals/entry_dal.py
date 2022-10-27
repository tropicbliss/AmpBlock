from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from helpers.db.models.entry import Entry
from helpers.model import Link


class EntryDal:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def save_entry(self, save_to_database, links: List[Link]):
        if save_to_database:
            data = [Entry(original_url=link.origin.url, canonical_url=link.canonical.url if link.canonical else None)
                    for link in links if link.origin and link.origin.is_amp]
            self.db_session.add_all(data)
            await self.db_session.flush()
        return

    async def get_entry_by_original_url(self, original_url):
        q = await self.db_session.execute(select(Entry).where(Entry.original_url == original_url).where(Entry.canonical_url != None).order_by(desc(Entry.entry_id)).limit(1))
        return q.scalars().first()
