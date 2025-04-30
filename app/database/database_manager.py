from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select, and_

from database.init_db import engine
from database.models import User, Transaction
from pass_hash import check_password, hash_password


class UserRepository:
    def __init__(self):
        self.session = async_sessionmaker(engine)
    
    async def _get_user_by_login(self, login: str):
        async with self.session() as session:
            result = await session.execute(select(User).where(User.login == login))
            return result.scalar_one_or_none()
    
    async def add_user(self, login: str, password: str):
        user = await self._get_user_by_login(login)
        if user:
            return False

        async with self.session() as session:
            password_hash = hash_password(password)
            user = User(login=login, password_hash=password_hash)
            session.add(user)
            await session.commit()
        return True
    
    async def check_user(self, login: str, password: str):
        user = await self._get_user_by_login(login)
        if user and check_password(password=password, hashed_password=user.password_hash):
            return user
        return False
    
    async def get_user_by_id(self, uid: int):
        async with self.session() as session:
            return await session.get(User, uid)
    
    async def get_user_id_by_login(self, login: str):
        user = await self._get_user_by_login(login)
        return user.id if user else None
    
    async def add_balance(self, uid: int, amount: int):
        async with self.session() as session:
            user = await session.get(User, uid)
            user.balance += amount
            await session.commit()
    
    async def get_balance_from_login(self, login: str):
        user = await self._get_user_by_login(login)
        return user.balance if user else None

class TransactionRepository:
    def __init__(self):
        self.session = async_sessionmaker(engine)
    
    async def _get_sender_and_receiver(self, session: AsyncSession, sender_login: str, receiver_login: str):
        sender = await session.execute(select(User).where(User.login == sender_login))
        sender = sender.scalar_one_or_none()
        receiver = await session.execute(select(User).where(User.login == receiver_login))
        receiver = receiver.scalar_one_or_none()
        return sender, receiver
    
    async def _update_transaction_status_in_history(self, session: AsyncSession, user: User, new_status: str):
        for transaction in user.history:
                if transaction['status'] == 'pending':
                    transaction['status'] = new_status
                    break
    
    async def _get_pending_transaction(self, session: AsyncSession, sender_login: str, receiver_login: str, amount: int):
        result = await session.execute(select(Transaction).where(
                and_(
                    Transaction.sender_login == sender_login, 
                    Transaction.receiver_login == receiver_login, 
                    Transaction.amount == amount, 
                    Transaction.status == 'pending'
                )
            ))
        return result.scalar()
    
    async def transfer_money(self, sender_login: str, receiver_login: str, amount: int):
        async with self.session() as session:
            sender, receiver = await self._get_sender_and_receiver(session, sender_login, receiver_login)
            sender.balance -= amount
            receiver.balance += amount
            
            transaction = await self._get_pending_transaction(session, sender_login, receiver_login, amount)
            if transaction:
                transaction.status = 'completed'
            
            await self._update_transaction_status_in_history(session, sender, 'completed')
            await self._update_transaction_status_in_history(session, receiver, 'completed')
            flag_modified(sender, 'history')
            flag_modified(receiver, 'history')
            await session.commit()
    
    async def unsuccessful_transaction(self, sender_login: str, receiver_login: str, amount: int):
        async with self.session() as session:
            transaction = await self._get_pending_transaction(session, sender_login, receiver_login, amount)
            if transaction:
                transaction.status = 'failed'
            
            sender, receiver = await self._get_sender_and_receiver(session, sender_login, receiver_login)
            await self._update_transaction_status_in_history(session, sender, 'failed')
            await self._update_transaction_status_in_history(session, receiver, 'failed')
            flag_modified(sender, 'history')
            flag_modified(receiver, 'history')
            await session.commit()
    
    async def add_transaction_to_history(self, sender_login: str, receiver_login: str, amount: int):
        async with self.session() as session:
            transaction = Transaction(
                sender_login=sender_login,
                receiver_login=receiver_login,
                amount=amount, 
                status='pending'
            )
            session.add(transaction)
            
            sender, receiver = await self._get_sender_and_receiver(session, sender_login, receiver_login)
            
            transaction_data = {
                'from': sender_login,
                'to': receiver_login,
                'amount': amount,
                'status': 'pending'
            }
            
            sender.history.append({**transaction_data, 'type': 'outgoing_transfer'})
            receiver.history.append({**transaction_data, 'type': 'incoming_transfer'})
            
            flag_modified(sender, 'history')
            flag_modified(receiver, 'history')
            await session.commit()