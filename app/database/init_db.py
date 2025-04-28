from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

import os

from database.models import Base


load_dotenv()

engine = create_async_engine(os.getenv('DB_PATH'))


class InitDataBase:
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)



