"""Фабрика маршрутов для прибора.

Для каждого прибора создаются эндпоинты:

=====================  ======  ==========================================
URL                    Метод   Назначение
=====================  ======  ==========================================
``/{slug}/``           GET     HTML-страница прибора
``/{slug}/``           POST    приём HTML-формы, редирект на страницу
``/api/{slug}/state``  GET     текущее состояние (JSON) для автообновления
``/api/{slug}/write``  POST    запись значений (JSON)
``/api/{slug}/logs``   GET     журнал статусов (JSON)
``/api/{slug}/poll``   POST    принудительный опрос прибора
=====================  ======  ==========================================
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.base import BaseDevice
from app.core.templating import templates


def build_router(device: BaseDevice) -> APIRouter:
    """Создать :class:`fastapi.APIRouter` для прибора ``device``."""
    router = APIRouter(tags=[device.title])
    slug = device.slug

    @router.get(f"/{slug}/", response_class=HTMLResponse, summary="Страница прибора")
    def page(request: Request, limit: int = Query(10, ge=1, le=100)):
        return templates.TemplateResponse(
            request,
            device.template,
            {
                "device": device,
                "state": device.read(),
                "logs": device.logs(limit),
                "limit": limit,
            },
        )

    @router.post(f"/{slug}/", summary="Приём HTML-формы")
    async def submit(request: Request):
        form = await request.form()
        values: dict[str, Any] = {k: form.get(k) for k in form.keys()}
        for flag in device.flags:
            values[flag] = flag in form
        device.apply(values)
        return RedirectResponse(f"/{slug}/", status_code=303)

    @router.get(f"/api/{slug}/state", summary="Текущее состояние прибора")
    def state() -> dict[str, Any]:
        return device.read()

    @router.post(f"/api/{slug}/write", summary="Записать значения в прибор")
    def write(payload: dict[str, Any] = Body(..., examples=[{"setpoint": 25.0}])):
        device.apply(payload)
        return device.read()

    @router.get(f"/api/{slug}/logs", summary="Журнал статусов")
    def logs(limit: int = Query(10, ge=1, le=100)) -> list[dict[str, str]]:
        return device.logs(limit)

    @router.post(f"/api/{slug}/poll", summary="Опросить устройство")
    def poll() -> dict[str, Any]:
        return device.poll()

    return router
