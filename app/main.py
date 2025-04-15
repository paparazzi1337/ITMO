import uuid
from decimal import Decimal
from database.database import get_session, init_db
from services.base_user_services import UserService
from services.balance_services import BalanceService
from services.model_services import ModelService
from services.prediction_history_services import PredictionService

def main():
    # Инициализация БД (только для разработки!)
    init_db()

    # Получаем сессию БД
    db = next(get_session())

    try:
        # 1. Инициализация сервисов
        user_service = UserService(db)
        balance_service = BalanceService(db)
        model_service = ModelService(db)
        prediction_service = PredictionService(db)

        # 2. Создание тестового пользователя
        user = user_service.create_user({
            'user_id': str(uuid.uuid4()),
            'username': 'test_user',
            'email': 'user@example.com',
            'password': 'securepassword123',
            'role': 'regular'
        })
        print(f"Создан пользователь: {user.username} ({user.role})")

        # 3. Пополнение баланса
        deposit_tx = balance_service.deposit(
            user=user,
            amount=Decimal('1000.00'),
            description="Initial deposit"
        )
        print(f"Пополнение баланса. ID транзакции: {deposit_tx}")
        print(f"Текущий баланс: {balance_service.get_balance(user)}")

        # 4. Создание модели
        model = model_service.create_model({
            'model_id': str(uuid.uuid4()),
            'name': 'Test Model',
            'owner_id': user.user_id,
            'model_type': 'tensorflow',
            'model_path': '/models/test'
        })
        print(f"Создана модель: {model.name}")

        # 5. Создание задачи предсказания
        prediction_task = prediction_service.create_task({
            'task_id': str(uuid.uuid4()),
            'user_id': user.user_id,
            'model_id': model.model_id,
            'input_data': {'param1': 1, 'param2': 2}
        })
        print(f"Создана задача предсказания: {prediction_task.task_id}")

        # 6. Завершение задачи предсказания
        prediction_service.complete_task(
            task_id=prediction_task.task_id,
            result={'output': 42}
        )
        print("Задача предсказания завершена")

        # 7. Проверка истории транзакций
        transactions = balance_service.get_transaction_history(user.user_id)
        print("\nИстория транзакций:")
        for tx in transactions:
            print(f"{tx['timestamp']} - {tx['type']}: {tx['amount']}")

    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()