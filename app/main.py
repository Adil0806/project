"""Главный файл приложения (разработчик: Аллагулов А. Р.).

Запуск::

    uvicorn app.main:app --reload

Swagger UI: ``/docs``, ReDoc: ``/redoc``.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.core.templating import templates
from app.modules import dz_so, io_module, pchv3, trm138

#: Подключённые модули. Чтобы добавить прибор — добавьте его сюда.
MODULES = [trm138, dz_so, pchv3, io_module]
DEVICES = [m.device for m in MODULES]

app = FastAPI(
    title="SCADA — команда 4",
    description="Учебная SCADA-система: ТРМ138, ДЗ-СО, ПЧВ3-К75-В, МВ110/МУ110.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
for module in MODULES:
    app.include_router(module.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    """Главная страница со списком приборов."""
    return templates.TemplateResponse(request, "index.html", {"devices": DEVICES})


@app.get("/api/devices", tags=["Система"], summary="Список приборов")
def list_devices() -> list[dict[str, str]]:
    """Вернуть описание всех подключённых приборов."""
    return [d.info() for d in DEVICES]


@app.get("/health", tags=["Система"], summary="Проверка работоспособности")
def health() -> dict[str, object]:
    """Healthcheck для Docker и мониторинга."""
    return {"status": "ok", "simulation": config.SIMULATION, "devices": len(DEVICES)}


templates.env.globals["nav"] = [d.info() for d in DEVICES]
