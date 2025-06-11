from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repository.user_repository import UserRepository
from database.repository.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.tx_repo = TransactionRepository(session)

    async def initiate_transfer(self, sender_login: str, receiver_login: str, amount: int):
        sender, receiver = await self.tx_repo.get_sender_and_receiver(sender_login, receiver_login)
        if not sender or not receiver:
            return False, 'User not found'

        if sender.balance < amount:
            return False, 'Insufficient funds'

        await self.tx_repo.create_transaction(sender_login, receiver_login, amount)

        history_data_sender = {
            'from': sender_login,
            'to': receiver_login,
            'amount': amount,
            'status': 'pending',
            'type': 'outgoing_transfer',
        }

        history_data_receiver = {
            'from': sender_login,
            'to': receiver_login,
            'amount': amount,
            'status': 'pending',
            'type': 'incoming_transfer',
        }

        await self.user_repo.update_history(sender, history_data_sender)
        await self.user_repo.update_history(receiver, history_data_receiver)

        await self.session.flush()
        return True, ''

    async def complete_transfer(self, sender_login: str, receiver_login: str, amount: int):
        sender, receiver = await self.tx_repo.get_sender_and_receiver(sender_login, receiver_login)
        transaction = await self.tx_repo.get_pending_transaction(sender_login, receiver_login, amount)

        if not sender or not receiver or not transaction:
            return False

        sender.balance -= amount
        receiver.balance += amount

        await self.tx_repo.update_transaction_status(transaction, 'completed')
        await self.tx_repo.update_transaction_history_status(sender, 'completed')
        await self.tx_repo.update_transaction_history_status(receiver, 'completed')

        await self.session.commit()
        return True

    async def fail_transfer(self, sender_login: str, receiver_login: str, amount: int):
        sender, receiver = await self.tx_repo.get_sender_and_receiver(sender_login, receiver_login)
        transaction = await self.tx_repo.get_pending_transaction(sender_login, receiver_login, amount)

        if not sender or not receiver or not transaction:
            return False

        await self.tx_repo.update_transaction_status(transaction, 'failed')
        await self.tx_repo.update_transaction_history_status(sender, 'failed')
        await self.tx_repo.update_transaction_history_status(receiver, 'failed')

        await self.session.commit()
        return True