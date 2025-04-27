from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select, and_

from database.init_db import engine
from database.models import User, Transaction
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
    return True

async def check_user(login: str, password: str):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.login==login))
        user = user.scalar_one_or_none()
        if user and check_password(password=password, hashed_password=user.password_hash):
            return user
        return False

async def get_user_by_id(uid: int):
    async with async_session() as session:
        user = await session.get(User, uid)
        return user

async def get_user_id_by_login(login: str):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.login==login))
        user = user.scalar_one_or_none()
        if user:
            return user.id
        return None

async def add_balance(uid: int, amount: int):
    async with async_session() as session:
        user = await session.get(User, uid)
        user.balance += amount
        await session.commit()

async def transfer_money(sender_login: str, receiver_login: str, amount: int):
    async with async_session() as session:
        sender = await session.execute(select(User).where(User.login==sender_login))
        sender = sender.scalar()
        
        receiver = await session.execute(select(User).where(User.login==receiver_login))
        receiver = receiver.scalar()
        
        sender.balance -= amount
        receiver.balance += amount
        
        transaction = await session.execute(select(Transaction).where(
            and_(
                Transaction.sender_login==sender_login, 
                Transaction.receiver_login==receiver_login, 
                Transaction.amount==amount, 
                Transaction.status=='pending'
            )
        ))
        transaction = transaction.scalar()
        transaction.status = 'completed'
        
        for sender_transaction in sender.history:
            print(sender_transaction)
            if sender_transaction['status'] == 'pending':
                sender_transaction['status'] = 'completed'
                break
        
        for receiver_transaction in receiver.history:
            if receiver_transaction['status'] == 'pending':
                receiver_transaction['status'] = 'completed'
                break
        flag_modified(sender, 'history')
        flag_modified(receiver, 'history')
        
        await session.commit()

async def unsuccessful_transaction(sender_login: str, receiver_login: str, amount: int):
    async with async_session() as session:
        sender = await session.execute(select(User).where(User.login==sender_login))
        sender = sender.scalar()

        receiver = await session.execute(select(User).where(User.login==receiver_login))
        receiver = receiver.scalar()
        
        transaction = await session.execute(select(Transaction).where(
            and_(
                Transaction.sender_login==sender_login, 
                Transaction.receiver_login==receiver_login, 
                Transaction.amount==amount, 
                Transaction.status=='pending'
            )
        ))
        transaction = transaction.scalar()
        transaction.status = 'unsuccessful'
        
        for sender_transaction in sender.history:
            if sender_transaction['status'] == 'pending':
                sender_transaction['status'] = 'failed'
                break
        
        for receiver_transaction in receiver.history:
            if receiver_transaction['status'] == 'pending':
                receiver_transaction['status'] = 'failed'
                break
        
        flag_modified(sender, 'history')
        flag_modified(receiver, 'history')
        
        await session.commit()

async def add_transaction_to_history(sender_login: str, receiver_login: str, amount: int):
    async with async_session() as session:
        transaction = Transaction(
            sender_login=sender_login,
            receiver_login=receiver_login,
            amount=amount, 
            status='pending'
        )
        session.add(transaction)
        
        sender = await session.execute(select(User).where(User.login==sender_login))
        sender = sender.scalar()
        
        receiver = await session.execute(select(User).where(User.login==receiver_login))
        receiver = receiver.scalar()
        
        transaction_data = {'from': sender_login, 'to': receiver_login, 'amount': amount, 'status': 'pending'}

        incoming_transaction = transaction_data.copy()
        incoming_transaction.update({'type': 'incoming_transfer'})
        
        outgoing_transaction = transaction_data.copy()
        outgoing_transaction.update({'type': 'outgoing_transfer'})
        
        sender.history.append(outgoing_transaction)
        receiver.history.append(incoming_transaction)
        flag_modified(sender, 'history')
        flag_modified(receiver, 'history')
        await session.commit()

async def get_balance_from_login(login: str):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.login==login))
        user = user.scalar()
        return user.balance