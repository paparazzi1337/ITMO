FROM python:3.11-slim

WORKDIR /app

# Копируем сначала requirements.txt
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app:/common

CMD ["python", "main.py"]