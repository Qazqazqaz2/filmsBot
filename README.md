# Movie Recommender Bot 🎬

Телеграм бот для изучения английского языка через фильмы. Бот рекомендует фильмы в соответствии с уровнем владения английским языком (A1-C2) и предоставляет ссылки на русские субтитры.

## Возможности 🚀

- Выбор уровня английского языка (A1-C2)
- Генерация рекомендаций фильмов с помощью GigaChat
- Автоматический поиск русских субтитров
- Сохранение истории рекомендаций в базе данных
- Отправка рекомендаций в тематические Telegram-каналы

## Установка 🛠

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Создайте и активируйте виртуальное окружение:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка ⚙️

1. Создайте файл `.env` и заполните его данными:
```env
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# GigaChat credentials
GIGACHAT_RQUID=your_rquid_here
GIGACHAT_AUTH=your_auth_here

# Telegram channel links
CHANNEL_LINK_A1=https://t.me/your_a1_channel
CHANNEL_LINK_A2=https://t.me/your_a2_channel
CHANNEL_LINK_B1=https://t.me/your_b1_channel
CHANNEL_LINK_B2=https://t.me/your_b2_channel
CHANNEL_LINK_C1=https://t.me/your_c1_channel
CHANNEL_LINK_C2=https://t.me/your_c2_channel

# Telegram channel IDs
CHANNEL_ID_A1=your_channel_id
CHANNEL_ID_A2=your_channel_id
CHANNEL_ID_B1=your_channel_id
CHANNEL_ID_B2=your_channel_id
CHANNEL_ID_C1=your_channel_id
CHANNEL_ID_C2=your_channel_id
```

2. Создайте каналы в Telegram для каждого уровня
3. Добавьте бота администратором в каждый канал
4. Получите ID каналов (можно через @getmyid_bot)

## Запуск 🚀

```bash
python run.py
```

## Структура проекта 📁

```
project/
├── src/
│   ├── __init__.py
│   ├── interfaces.py          # Интерфейсы сервисов
│   ├── bot.py                # Основной класс бота
│   └── services/             # Реализации сервисов
│       ├── __init__.py
│       ├── gigachat_service.py    # Сервис рекомендаций
│       ├── subtitle_service.py     # Поиск субтитров
│       ├── channel_service.py      # Управление каналами
│       └── database_service.py     # Работа с БД
├── .env                      # Конфигурация
├── .gitignore               # Игнорируемые файлы
├── requirements.txt         # Зависимости проекта
└── run.py                  # Точка входа
```

## Использование 📱

1. Запустите бота командой `/start`
2. Выберите уровень владения английским
3. Получите доступ к каналу с подборками фильмов
4. Используйте кнопку "Сгенерировать" для получения новых рекомендаций

## Технологии 💻

- Python 3.7+
- aiogram (Telegram Bot API)
- GigaChat API (генерация рекомендаций)
- SQLite (хранение истории)
- aiosqlite (асинхронная работа с БД)
- BeautifulSoup4 (парсинг субтитров)

## Примечания 📝

- База данных (`movies.db`) создается автоматически при первом запуске
- В каждом канале хранятся рекомендации только соответствующего уровня
- При показе истории отображаются только 5 последних рекомендаций
- При зависании страницы с субтитрами рекомендуется её перезагрузить

## Лицензия 📄

MIT License 