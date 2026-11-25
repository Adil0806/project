# SCADA — команда 4

Web-интерфейсы промышленных приборов на FastAPI + Jinja2 + Bootstrap.

| Прибор | Назначение | Модуль |
|---|---|---|
| ТРМ138 | КИП | `app/modules/trm138.py` |
| ДЗ-СО | Датчик загазованности (CO) | `app/modules/dz_so.py` |
| ПЧВ3-К75-В | Преобразователь частоты | `app/modules/pchv3.py` |
| МВ110-224.2А + МУ110-224.6У | IO-модуль | `app/modules/io_module.py` |

## Запуск
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Приложение: http://localhost:8000 · Swagger UI: `/docs` · ReDoc: `/redoc`

## Структура
```
app/
├── main.py        # главный файл
├── config.py      # настройки
├── core/          # базовый класс прибора, маршруты, шаблонизатор
├── modules/       # модули приборов
├── templates/     # Jinja2-шаблоны
└── static/        # стили, скрипты, изображения
tests/             # pytest
docs/              # Sphinx
```

## Эндпоинты прибора (`slug`: trm138, dz-so, pchv3, io)
| URL | Метод | Назначение |
|---|---|---|
| `/{slug}/` | GET, POST | страница, приём формы |
| `/api/{slug}/state` | GET | состояние (JSON) |
| `/api/{slug}/write` | POST | запись значений |
| `/api/{slug}/logs` | GET | журнал статусов |
| `/api/{slug}/poll` | POST | опрос прибора |
| `/api/devices`, `/health` | GET | список приборов, healthcheck |

## Тесты и документация
```bash
pytest
sphinx-build -b html docs docs/_build
```

## Docker
```bash
docker compose up --build
```
