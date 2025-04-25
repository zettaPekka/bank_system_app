from fastapi import FastAPI
import uvicorn
import asyncio

import logging

from routers.routers import router
from database.init_db import init_database
from bank_transactions.init_worker import start_worker


logging.basicConfig(level=logging.INFO)

app = FastAPI() 
app.include_router(router)

async def main():
    config = uvicorn.Config('main:app', reload=True)
    server = uvicorn.Server(config)
    
    await init_database()
    asyncio.create_task(start_worker())
    
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())