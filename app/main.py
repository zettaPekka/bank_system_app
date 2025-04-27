from fastapi import FastAPI
import uvicorn
import asyncio

import logging

from routers.routers import router
from database.init_db import init_database


logging.basicConfig(level=logging.INFO)

app = FastAPI() 
app.include_router(router)

async def main():
    await init_database()


if __name__ == '__main__':
    try:
        asyncio.run(main())
        uvicorn.run('main:app', reload=True)
    except KeyboardInterrupt:
        pass
