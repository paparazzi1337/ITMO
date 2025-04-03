FROM python:3.9

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

EXPOSE 8080
# Копируем остальной код
COPY ./ /app

CMD ["python", "main.py"]