from models.base_user import BaseUser, RegularUser, ModelOwnerUser, AdminUser, UserRole
from models.balance import Balance, Transaction, BalanceService, TransactionType
from models.model import TensorFlowModel
from models.prediction_history import PredictionTask, PredictionHistory, PredictionStatus
import uuid
from decimal import Decimal
from datetime import datetime
from database.database import engine, SessionLocal, Base

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

def create_users(session):
    # Create different types of users
    regular_user = RegularUser(
        user_id=str(uuid.uuid4()),
        username="regular_user",
        email="regular@example.com",
        password="regular123"
    )
    
    model_owner = ModelOwnerUser(
        user_id=str(uuid.uuid4()),
        username="model_owner",
        email="owner@example.com",
        password="owner123"
    )
    
    admin = AdminUser(
        user_id=str(uuid.uuid4()),
        username="admin",
        email="admin@example.com",
        password="admin123"
    )
    
    # Add users to session
    session.add_all([regular_user, model_owner, admin])
    session.commit()
    
    return regular_user, model_owner, admin

def demo_balance_operations(session, users):
    regular_user, model_owner, admin = users
    balance_service = BalanceService(session)
    
    # Deposit money to users
    print("\nDepositing money to users:")
    tx1 = balance_service.deposit(regular_user.user_id, Decimal('1000.00'), "Initial deposit")
    tx2 = balance_service.deposit(model_owner.user_id, Decimal('2000.00'), "Initial deposit")
    tx3 = balance_service.deposit(admin.user_id, Decimal('3000.00'), "Initial deposit")
    
    # Check balances
    print("\nUser balances:")
    print(f"Regular user balance: {balance_service.get_balance(regular_user.user_id)}")
    print(f"Model owner balance: {balance_service.get_balance(model_owner.user_id)}")
    print(f"Admin balance: {balance_service.get_balance(admin.user_id)}")
    
    # Make a payment
    print("\nMaking payment from regular user:")
    payment_tx = balance_service.make_payment(
        regular_user.user_id,
        Decimal('150.00'),
        "Model prediction service"
    )
    print(f"Payment transaction ID: {payment_tx}")
    
    # Check balance after payment
    print(f"Regular user balance after payment: {balance_service.get_balance(regular_user.user_id)}")
    
    # Show transaction history
    print("\nRegular user transaction history:")
    history = balance_service.get_transaction_history(regular_user.user_id)
    for tx in history:
        print(f"{tx['timestamp']} - {tx['type']}: {tx['amount']} ({tx['status']})")

def main():
    init_db()
    db = SessionLocal()
    
    try:
        # Create users
        users = create_users(db)
        
        # Demo balance operations
        demo_balance_operations(db, users)
        
        # Commit all changes
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()