from fastapi import FastAPI
import uvicorn
import asyncio

from routers.routers import router
from database.init_db import init_database


app = FastAPI() 
app.include_router(router)


if __name__ == '__main__':
    asyncio.run(init_database())
    uvicorn.run('main:app', reload=True)
