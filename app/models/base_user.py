from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.database import Base
import bcrypt
import re

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
    predictions = relationship("PredictionTask", back_populates="user")
    models = relationship("MLModel", back_populates="owner")

    def __init__(self, user_id: str, username: str, email: str, password : str, role: UserRole):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password = password
        self._role = role

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def validate_email(self) -> bool:
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not pattern.match(self.email):
            raise ValueError("Неверный формат электронной почты")
        return True    

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self._password_hash.encode('utf-8')
        )
    
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email
    
    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deactivate(self) -> None:
        self._is_active = False

    def can_perform_action(self, action: str) -> bool:
        raise NotImplementedError("Метод должен быть переопределен в дочерних классах")

    def __str__(self) -> str:
        return f"User {self._username} ({self._role.value})"

class RegularUser(BaseUser):
    def __init__(self, user_id: str, username: str, email: str):
        super().__init__(user_id, username, email, UserRole.REGULAR)

    def can_perform_action(self, action: str) -> bool:
        return action in ["make_prediction", "view_history"]

class ModelOwnerUser(BaseUser):
    def __init__(self, user_id: str, username: str, email: str):
        super().__init__(user_id, username, email, UserRole.MODEL_OWNER)

    def can_perform_action(self, action: str) -> bool:
        return action in ["make_prediction", "view_history", "upload_model", "manage_model"]

class AdminUser(BaseUser):
    def __init__(self, user_id: str, username: str, email: str):
        super().__init__(user_id, username, email, UserRole.ADMIN)

    def can_perform_action(self, action: str) -> bool:
        return True