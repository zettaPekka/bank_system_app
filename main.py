from fastapi import FastAPI
import uvicorn
import asyncio

import logging

from routers.routers import router
from database.init_db import init_database


logging.basicConfig(level=logging.INFO)

app = FastAPI() 
app.include_router(router)


if __name__ == '__main__':
    asyncio.run(init_database())
    uvicorn.run('main:app', reload=True)
