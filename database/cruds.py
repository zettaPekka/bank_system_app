from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from database.init_db import engine
from database.models import User
from pass_hash import check_password, hash_password


async_session = async_sessionmaker(engine)

async def add_user(login: str, password: str):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.login==login))
        user = user.scalar_one_or_none()
        if user:
            return False
        password_hash = hash_password(password)
        user = User(login=login, password_hash=password_hash)
        session.add(user)
        await session.commit()

async def check_user(login: str, password: str):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.login==login))
        user = user.scalar_one_or_none()
        if user and check_password(password=password, hashed_password=user.password_hash):
            return True
        return False
