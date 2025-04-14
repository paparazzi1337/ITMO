from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Dict
from sqlalchemy import Column, String, JSON, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class MLModelStatus(Enum):
    TRAINING = "training"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class BaseMLModel(Base):
    __tablename__ = "models"

    model_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    status = Column(SQLEnum(MLModelStatus), default=MLModelStatus.INACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    model_type = Column(String, nullable=False)
    model_path = Column(String)

    owner = relationship("BaseUser", back_populates="models")
    predictions = relationship("PredictionTask", back_populates="model")

    def __init__(self, model_id: str, name: str, owner_id: str):
        self._model_id = model_id
        self._name = name
        self._owner_id = owner_id
        self._status = MLModelStatus.INACTIVE
        self._created_at = datetime.now()
        self._metadata: Dict[str, str] = {}
        self.model_type = "base"

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def owner_id(self) -> str:
        return self._owner_id

    @property
    def status(self) -> MLModelStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def metadata(self) -> Dict[str, str]:
        return self._metadata.copy()

    def update_metadata(self, key: str, value: str) -> None:
        self._metadata[key] = value

    def remove_metadata(self, key: str) -> None:
        self._metadata.pop(key, None)

    def activate(self) -> None:
        self._status = MLModelStatus.ACTIVE

    def deactivate(self) -> None:
        self._status = MLModelStatus.INACTIVE

    def predict(self, input_data: Dict) -> Dict:
        raise NotImplementedError("Метод должен быть переопределен в дочерних классах")

    def __str__(self) -> str:
        return f"ML Model {self._name} ({self._status.value})"

class TensorFlowModel(BaseMLModel):
    def __init__(self, model_id: str, name: str, owner_id: str, model_path: str):
        super().__init__(model_id, name, owner_id)
        self._model_path = model_path
        self.model_type = "tensorflow"
        self._model = self._load_model()

    def _load_model(self):
        # Реальная загрузка модели

        '''
        model = load_model(self._model_path)
        return model
        '''


        print(f"Loading TensorFlow model from {self._model_path}")
        return None  # В реальности здесь будет загруженная модель

    def predict(self, input_data: Dict) -> Dict:
        if self._status != MLModelStatus.ACTIVE:
            raise ValueError("Model is not active")
        
        # Здесь будет реальное предсказание
        print(f"Making prediction with TensorFlow model {self._name}")
        return {"prediction": "sample_result"}