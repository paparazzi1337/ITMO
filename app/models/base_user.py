from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.database import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    REGULAR = "regular"
    MODEL_OWNER = "model_owner"

class BaseUser(Base):
    __tablename__ = "users"

    _user_id = Column("user_id", String, primary_key=True)
    _username = Column("username", String, unique=True, nullable=False)
    _email = Column("email", String, unique=True, nullable=False)
    _password = Column("password", String, nullable=False)
    _role = Column("role", SQLEnum(UserRole), nullable=False)
    _created_at = Column("created_at", DateTime, default=datetime.now)
    _is_active = Column("is_active", Boolean, default=True)

    balance = relationship("Balance", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    predictions = relationship("PredictionTask", back_populates="user")
    models = relationship("MLModel", back_populates="owner")