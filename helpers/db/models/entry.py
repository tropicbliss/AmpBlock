from sqlalchemy import Column, Integer, VARCHAR
from helpers.db.config import Base


class Entry(Base):
    __tablename__ = "URLConversions"
    entry_id = Column('entry_id', Integer,
                      primary_key=True, autoincrement=True)
    original_url = Column('original_url', VARCHAR(4000))
    canonical_url = Column('canonical_url', VARCHAR(4000))
