from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import JSON


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    balance: Mapped[int] = mapped_column(default=0)
    history: Mapped[list] = mapped_column(JSON, default=[])

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int]
    receiver_id: Mapped[int]
    amount: Mapped[int]
    status: Mapped[str]

class Deposit(Base):
    __tablename__ = 'deposits'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    amount: Mapped[int]
    end_data: Mapped[str]