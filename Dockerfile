# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы из текущей папки в контейнер
COPY . .

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 80 (на нём запускается бот)
EXPOSE 80

# Указываем команду для запуска бота
CMD ["python", "bot.py"]

