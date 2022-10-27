from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import helpers.static as static

DATABASE_URL = "mysql+mysqlconnector://{username}:{password}@" \
    "{hostname}/{databasename}".format(
        username=static.DB_USERNAME,
        password=static.DB_PASSWORD,
        hostname=static.DB_HOSTNAME,
        databasename=static.DB_DATABASENAME)

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
