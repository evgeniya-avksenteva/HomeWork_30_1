# Указываем базовый образ
FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем остальные файлы проекта в контейнер
COPY . /app/

# Открываем порт 8000 для взаимодействия с приложением
RUN mkdir -p /app/static

# Определяем команду для запуска приложения
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
