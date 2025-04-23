from pydantic import BaseModel, EmailStr, ConfigDict, SecretStr
from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# User schemas
class UserRole(str, Enum):
    ADMIN = "admin"
    REGULAR = "regular"
    MODEL_OWNER = "model_owner"

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Balance schemas
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionCreate(BaseModel):
    amount: Decimal
    description: Optional[str] = None

class TransactionResponse(TransactionCreate):
    id: str
    user_id: str
    type: TransactionType
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    amount: Decimal
    updated_at: datetime

    class Config:
        from_attributes = True

# Model schemas
class MLModelStatus(str, Enum):
    TRAINING = "training"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class ModelBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str
    model_type: str

class ModelCreate(ModelBase):
    pass

class ModelResponse(ModelBase):
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes = True
    )

    model_id: str
    owner_id: str
    status: MLModelStatus
    created_at: datetime
        

# Prediction schemas
class PredictionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PredictionCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    input_data: dict

class PredictionResponse(PredictionCreate):
    task_id: str
    user_id: str
    status: PredictionStatus
    created_at: datetime
    result: Optional[dict] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True