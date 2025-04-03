from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

class PredictionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PredictionTask:
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
    def __init__(self):
        self._history: List[PredictionTask] = []

    def add_task(self, task: PredictionTask) -> None:
        self._history.append(task)

    def get_user_history(self, user_id: str) -> List[PredictionTask]:
        # В реальной реализации здесь будет фильтрация по пользователю
        return [task for task in self._history]

    def get_model_history(self, model_id: str) -> List[PredictionTask]:
        return [task for task in self._history if task.model_id == model_id]

    def get_task_by_id(self, task_id: str) -> Optional[PredictionTask]:
        for task in self._history:
            if task.task_id == task_id:
                return task
        return None