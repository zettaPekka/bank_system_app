from fastapi import FastAPI
import uvicorn
import asyncio

import logging

from routers.user_router import router
from database.init_db import InitDataBase


logging.basicConfig(level=logging.INFO)

app = FastAPI() 
app.include_router(router)

async def main():
    await InitDataBase.init_db()


if __name__ == '__main__':
    try:
        asyncio.run(main())
        uvicorn.run('main:app', reload=True)
    except KeyboardInterrupt:
        pass
