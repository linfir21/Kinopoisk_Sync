# 

Синхронизация фильмов и сериалов с Кинопоиска. Парсит списки «просмотрено» и «буду смотреть» для двух пользователей, показывает совпадения фильмов, для общего просмотра и позволяет фильтровать по оценкам.

## Функции

- Парсинг через Playwright ( Chromium ) с авторизацией/капчей
- Поддержка фильмов **и** сериалов
- Постраничный обход списков Кинопоиска
- Обогащение данных через [Kinopoisk API Unofficial](https://kinopoiskapiunofficial.tech)
- Django-сайт со спойлерами и фильтром по оценкам
- Совпадения между пользователями

## Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/linfir21/Kinopoisk_Sync.git
cd kinopoisk_sync

# 2. Создать виртуальное окружение
python -m venv venv

# Windows:
source venv/Scripts/activate
# Linux/macOS:
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Установить браузеры для Playwright
playwright install chromium
```

## Настройка .env

Создай файл `.env` в корне проекта и добавь:

```env
# ID пользователей Кинопоиска (берётся из URL профиля)
KP_USER1_ID=12345678
KP_USER2_ID=87654321

# Имена пользователей (для отображения на сайте)
KP_USER1_NAME=Имя
KP_USER2_NAME=Имя второго

# API-ключ с kinopoiskapiunofficial.tech
KP_API_KEY=your_api_key_here

# Выглядеть должно так
"KP_USER1_ID=12345678
KP_USER1_NAME=Имя
KP_USER2_ID=87654321
KP_USER2_NAME=Имя второго
KP_API_KEY=your_api_key_here"

```

> **Где взять ID?**  
> Открой профиль на Кинопоиске — URL будет вида `https://www.kinopoisk.ru/user/12345678/`. Цифры — это ID.

> **Где взять API-ключ?**  
> Регистрация бесплатная на [kinopoiskapiunofficial.tech](https://kinopoiskapiunofficial.tech). Бесплатный тариф обычно даёт ~500 запросов в сутки.

## Запуск

### Миграции
```bash
python manage.py migrate
```

### Парсинг списков с Кинопоиска
```bash
python manage.py parse_kp
```

Браузер откроется визуально (`headless=False`), чтобы можно было решить капчу вручную, если она появится.

### Обогащение данных (описания, жанры, рейтинги, актёры)
```bash
python manage.py enrich_movies
```

Обрабатывает фильмы без описания. Можно ограничить количество:
```bash
python manage.py enrich_movies --limit 100
```

### Запуск веб-интерфейса
```bash
python manage.py runserver
```

Сайт будет доступен по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Полезные команды

| Команда | Описание |
|---------|----------|
| `python manage.py parse_kp` | Спарсить «просмотрено» и «буду смотреть» |
| `python manage.py enrich_movies` | Дополнить фильмы данными из API |
| `python manage.py runserver` | Запустить сайт |
| `python manage.py migrate` | Применить миграции |
| `python manage.py createsuperuser` | Создать администратора | Это по сути и не нужно

## Структура проекта

```
kinopoisk_sync/
├── config.py           # Конфигурация и .env
├── db.py               # Работа с SQLite
├── parser.py           # Парсер Кинопоиска (Playwright)
├── enricher.py         # Обогащение через Kinopoisk API
├── manage.py           # Django
├── requirements.txt    # Зависимости
├── .env                # Переменные окружения (не коммитить!)
├── movies/             # Django-приложение
│   ├── models.py       # Модели Movie и UserMovie
│   ├── views.py        # Логика отображения
│   ├── templates/      # HTML-шаблоны
│   └── management/     # Кастомные команды
├── static/             # CSS
└── movies.db           # SQLite база
```

## Лицензия

Для личного использования.
