# Weather_for_CU Bot

Weather_for_CU — это Telegram-бот, который предоставляет прогноз погоды для заданных координат. Пользователи могут выбрать количество дней для прогноза и указать координаты точек, для которых они хотят получить информацию о погоде.

## Установка

1. **Клонируйте репозиторий:**

```bash
git clone https://github.com/USERNAME/REPOSITORY_NAME.git
cd REPOSITORY_NAME
```

2. **Создайте виртуальное окружение (опционально):**
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate  # Для Windows
```

3. **Установите зависимости: Убедитесь, что у вас установлен Python 3.7 или выше. Затем выполните:**
```bash
pip install -r requirements.txt
```

# Использование
1. **Запустите бота**
```bash
python bot.py
```
2. **Откройте телеграмм и найди бота по имени Weather_for_CU**
3. **Нажмите кнопку "Start" и следуйте инструкциям для получения прогноза погоды**

# Команды
/start — Начать взаимодействие с ботом.
/help — Получить информацию о функционале бота.
/coordinat — Узнать, как вводить координаты.

# Структура проекта
bot.py — Основной файл с кодом бота.
help_message.txt — Файл с сообщением помощи.
About_coords.txt — Файл с информацией о вводе координат.
webserver.py — Файл с функцией для обработки данных о погоде (если используется).