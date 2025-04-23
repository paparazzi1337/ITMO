'''import pika
import json
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.model import BaseMLModel
from models.prediction_history import PredictionTask

def start_worker():
    # Инициализация подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    
    # Загрузка моделей (пример для TensorFlow)
    loaded_models = {}
    
    def load_model(model_id: str):
        """Ленивая загрузка модели по требованию"""
        if model_id not in loaded_models:
            db = SessionLocal()
            model = db.query(BaseMLModel).filter(
                BaseMLModel.model_id == model_id
            ).first()
            
            if model.model_type == 'tensorflow':
                loaded_models[model_id] = TensorFlowModelService(model.model_path)
            # Добавьте другие типы моделей по необходимости
            
        return loaded_models.get(model_id)
    
    def callback(ch, method, properties, body):
        db = SessionLocal()
        try:
            data = json.loads(body)
            model = load_model(data['model_id'])
            
            if not model:
                raise ValueError(f"Model {data['model_id']} not found")
            
            # Выполнение предсказания
            result = model.predict(data['input_data'])
            
            # Сохранение результата
            prediction = PredictionTask(
                task_id=data['task_id'],
                user_id=data.get('user_id'),
                model_id=data['model_id'],
                input_data=data['input_data'],
                prediction_result=result,
                status='completed'
            )
            db.add(prediction)
            db.commit()
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing task: {e}")
            db.rollback()
            ch.basic_nack(delivery_tag=method.delivery_tag)
        finally:
            db.close()
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='model_predictions',
        on_message_callback=callback
    )
    
    print("ML Worker started. Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()'''