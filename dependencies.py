from helpers.db.config import async_session
from helpers.db.dals.entry_dal import EntryDal


async def get_entry_dal():
    async with async_session() as session:
        async with session.begin():
            yield EntryDal(session)
