from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm.attributes import flag_modified

from database.models import Transaction, User


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_sender_and_receiver(self, sender_login: str, receiver_login: str):
        sender_result = await self.session.execute(
            select(User).where(User.login == sender_login)
        )
        receiver_result = await self.session.execute(
            select(User).where(User.login == receiver_login)
        )
        return sender_result.scalar_one_or_none(), receiver_result.scalar_one_or_none()

    async def create_transaction(self, sender_login: str, receiver_login: str, amount: int):
        transaction = Transaction(
            sender_login=sender_login,
            receiver_login=receiver_login,
            amount=amount,
            status='pending',
        )
        self.session.add(transaction)
        return transaction

    async def get_pending_transaction(self, sender_login: str, receiver_login: str, amount: int):
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.sender_login == sender_login,
                    Transaction.receiver_login == receiver_login,
                    Transaction.amount == amount,
                    Transaction.status == 'pending',
                )
            ).order_by(Transaction.id).limit(1) 
        )
        return result.scalar_one_or_none()

    async def update_transaction_status(self, transaction: Transaction, new_status: str):
        transaction.status = new_status

    async def update_transaction_history_status(self, user: User, new_status: str):
        for tx in user.history:
            if tx['status'] == 'pending':
                tx['status'] = new_status
                break
        flag_modified(user, 'history')