import uuid
from datetime import datetime
from typing import Dict, List
from enum import Enum
from decimal import Decimal
import threading

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class InsufficientFundsError(Exception):
    pass

class TransactionNotFoundError(Exception):
    pass

class BalanceService:
    def __init__(self):
        self._balances: Dict[str, Decimal] = {}  # user_id -> balance
        self._transactions: Dict[str, Dict] = {}  # transaction_id -> transaction_data
        self._lock = threading.Lock()  # Для потокобезопасности

    def get_balance(self, user_id: str) -> Decimal:
        """Возвращает текущий баланс пользователя."""
        return self._balances.get(user_id, Decimal('0'))

    def deposit(self, user_id: str, amount: Decimal, description: str = "") -> str:
        """Пополняет баланс пользователя."""
        with self._lock:
            if user_id not in self._balances:
                raise ValueError(f"User {user_id} has no account")
            
            if amount <= Decimal('0'):
                raise ValueError("Amount must be positive")

            transaction_id = self._log_transaction(
                user_id=user_id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=description,
                status=TransactionStatus.PENDING
            )

            try:
                self._balances[user_id] += amount
                self._transactions[transaction_id]['status'] = TransactionStatus.COMPLETED
                return transaction_id
            except Exception as e:
                self._transactions[transaction_id]['status'] = TransactionStatus.FAILED
                self._transactions[transaction_id]['error'] = str(e)
                raise

    def make_payment(
        self,
        user_id: str,
        amount: Decimal,
        service_name: str,
        reference_id: str = None
    ) -> str:
        """Обрабатывает платеж за использование сервиса."""
        description = f"Payment for {service_name}"
        if reference_id:
            description += f" (ref: {reference_id})"
        
        return self.withdraw(
            user_id=user_id,
            amount=amount,
            description=description
        )

    def get_transaction_history(self, user_id: str) -> List[Dict]:
        """Возвращает историю транзакций пользователя."""
        return [
            tx for tx in self._transactions.values()
            if tx['user_id'] == user_id
        ]

    def _log_transaction(
        self,
        user_id: str,
        amount: Decimal,
        transaction_type: TransactionType,
        description: str = "",
        status: TransactionStatus = TransactionStatus.COMPLETED
    ) -> str:
        """Логирует транзакцию и возвращает её ID."""
        transaction_id = f"tx_{uuid.uuid4().hex}"
        
        self._transactions[transaction_id] = {
            'id': transaction_id,
            'user_id': user_id,
            'amount': float(amount),  # Для JSON-сериализации
            'type': transaction_type.value,
            'description': description,
            'status': status.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return transaction_id