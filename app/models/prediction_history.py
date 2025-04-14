from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from sqlalchemy import Column, String, JSON, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class PredictionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PredictionTask(Base):
    __tablename__ = "predictions"

    task_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    model_id = Column(String, ForeignKey("models.model_id"))
    input_data = Column(JSON)
    status = Column(SQLEnum(PredictionStatus), default=PredictionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    result = Column(JSON)
    error = Column(String)
    
    user = relationship("BaseUser", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")

    def __init__(self, task_id: str, model_id: str, input_data: Dict):
        self._task_id = task_id
        self._model_id = model_id
        self._input_data = input_data
        self._status = PredictionStatus.PENDING
        self._created_at = datetime.now()
        self._result: Optional[Dict] = None
        self._error: Optional[str] = None

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def input_data(self) -> Dict:
        return self._input_data.copy()

    @property
    def status(self) -> PredictionStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def result(self) -> Optional[Dict]:
        return self._result

    @property
    def error(self) -> Optional[str]:
        return self._error

    def complete(self, result: Dict) -> None:
        self._result = result
        self._status = PredictionStatus.COMPLETED

    def fail(self, error: str) -> None:
        self._error = error
        self._status = PredictionStatus.FAILED

    def __str__(self) -> str:
        return f"Task {self._task_id} for model {self._model_id} ({self._status.value})"

class PredictionHistory:
    def __init__(self, db_session):
        self.db = db_session

    def add_task(self, task: PredictionTask) -> None:
        self.db.add(task)
        self.db.commit()

    def get_user_history(self, user_id: str) -> List[PredictionTask]:
        return self.db.query(PredictionTask)\
            .filter(PredictionTask.user_id == user_id)\
            .order_by(PredictionTask.created_at.desc())\
            .all()

    def get_model_history(self, model_id: str) -> List[PredictionTask]:
        return self.db.query(PredictionTask)\
            .filter(PredictionTask.model_id == model_id)\
            .order_by(PredictionTask.created_at.desc())\
            .all()

    def get_task_by_id(self, task_id: str) -> Optional[PredictionTask]:
        return self.db.query(PredictionTask)\
            .filter(PredictionTask.task_id == task_id)\
            .first()