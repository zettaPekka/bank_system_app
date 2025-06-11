from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from pass_hash import hash_password, check_password
from database.models import User
from database.repository.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, login: str, password: str) -> bool:
        existing_user = await self.user_repo.get_user_by_login(login)
        if existing_user:
            return False
        password_hash = hash_password(password)
        await self.user_repo.create_user(login, password_hash)
        await self.session.commit()
        return True

    async def authenticate_user(self, login: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_user_by_login(login)
        if user and check_password(password, user.password_hash):
            return user
        return None

    async def get_user_balance(self, login: str) -> Optional[int]:
        return await self.user_repo.get_balance_by_login(login)

    async def add_balance_to_user(self, user: User, amount: int):
        await self.user_repo.update_balance(user, amount)