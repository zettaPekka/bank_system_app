from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select

from database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_login(self, login: str):
        result = await self.session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    async def create_user(self, login: str, password_hash: str):
        user = User(login=login, password_hash=password_hash)
        self.session.add(user)
        return user

    async def get_user_by_id(self, uid: int):
        return await self.session.get(User, uid)

    async def update_balance(self, user: User, amount: int):
        user.balance += amount

    async def get_balance_by_login(self, login: str):
        user = await self.get_user_by_login(login)
        return user.balance if user else None

    async def update_history(self, user: User, history_data: dict):
        print(user.login, history_data['type'])
        user.history.append(history_data)
        flag_modified(user, 'history')
