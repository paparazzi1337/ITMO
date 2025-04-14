from decimal import Decimal
from enum import Enum
from uuid import uuid4
from datetime import datetime
from typing import List, Dict
import threading
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Numeric, Enum as SQLEnum, DateTime, ForeignKey
from database.database import Base

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class InsufficientFundsError(Exception):
    pass

class TransactionNotFoundError(Exception):
    pass

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: f"tx_{uuid4().hex}")
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Numeric(precision=20, scale=2), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False)
    description = Column(String)
    error = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Balance(Base):
    __tablename__ = "balances"

    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)
    amount = Column(Numeric(precision=20, scale=2), default=Decimal('0'), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BalanceService:
    def __init__(self, db: Session):
        self.db = db
        self._lock = threading.Lock()

    def get_balance(self, user_id: str) -> Decimal:
        balance = self.db.query(Balance).filter(Balance.user_id == user_id).first()
        return balance.amount if balance else Decimal('0')

    def deposit(self, user_id: str, amount: Decimal, description: str = "") -> str:
        if amount <= Decimal('0'):
            raise ValueError("Amount must be positive")

        with self._lock:
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type=TransactionType.DEPOSIT,
                status=TransactionStatus.PENDING,
                description=description
            )
            self.db.add(transaction)

            balance = self.db.query(Balance).filter(Balance.user_id == user_id).first()
            if not balance:
                balance = Balance(user_id=user_id, amount=Decimal('0'))
                self.db.add(balance)

            balance.amount += amount
            transaction.status = TransactionStatus.COMPLETED
            self.db.commit()
            return transaction.id

    def withdraw(self, user_id: str, amount: Decimal, description: str = "") -> str:
        if amount <= Decimal('0'):
            raise ValueError("Amount must be positive")

        with self._lock:
            balance = self.db.query(Balance).filter(Balance.user_id == user_id).first()
            if not balance or balance.amount < amount:
                raise InsufficientFundsError("Insufficient funds")

            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.PENDING,
                description=description
            )
            self.db.add(transaction)

            balance.amount -= amount
            transaction.status = TransactionStatus.COMPLETED
            self.db.commit()
            return transaction.id

    def make_payment(self, user_id: str, amount: Decimal, service_name: str, reference_id: str = None) -> str:
        description = f"Payment for {service_name}"
        if reference_id:
            description += f" (ref: {reference_id})"
        
        return self.withdraw(
            user_id=user_id,
            amount=amount,
            description=description
        )

    def get_transaction_history(self, user_id: str) -> List[Dict]:
        transactions = self.db.query(Transaction)\
            .filter(Transaction.user_id == user_id)\
            .order_by(Transaction.timestamp.desc())\
            .all()
        
        return [{
            'id': tx.id,
            'amount': tx.amount,
            'type': tx.type,
            'description': tx.description,
            'status': tx.status,
            'timestamp': tx.timestamp.isoformat()
        } for tx in transactions]

    def get_transaction(self, transaction_id: str) -> Dict:
        transaction = self.db.query(Transaction)\
            .filter(Transaction.id == transaction_id)\
            .first()
        
        if not transaction:
            raise TransactionNotFoundError(f"Transaction {transaction_id} not found")
        
        return {
            'id': transaction.id,
            'user_id': transaction.user_id,
            'amount': transaction.amount,
            'type': transaction.type,
            'status': transaction.status,
            'description': transaction.description,
            'timestamp': transaction.timestamp.isoformat()
        }