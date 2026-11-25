"""Преобразователь частоты: ПЧВ3-К75-В (Modbus RTU).

Разработчик: Альмуханов А. М. (ветка ``feature/pchv3``).
"""
from __future__ import annotations

import time
from typing import Any

from app.core.base import BaseDevice, to_float
from app.core.routing import build_router

MAX_FREQ = 50.0
RAMP_HZ_PER_S = 10.0


class Pchv3(BaseDevice):
    """Частотный преобразователь: уставка частоты, пуск/стоп, реверс."""

    slug = "pchv3"
    title = "ПЧВ3-К75-В"
    model = "ПЧВ3-К75-В"
    description = "Преобразователь частоты 0,75 кВт"
    template = "pchv3.html"
    image = "/static/img/pchv3.svg"
    flags = ("run", "reverse")

    def __init__(self) -> None:
        super().__init__()
        self._setpoint = 25.0
        self._run = False
        self._reverse = False
        self._freq = 0.0
        self._last = time.monotonic()
        self._status = "Остановлен"

    def _step(self) -> None:
        """Симуляция разгона/торможения по линейной рампе."""
        now = time.monotonic()
        dt, self._last = now - self._last, now
        target = self._setpoint if self._run else 0.0
        delta = RAMP_HZ_PER_S * dt
        if self._freq < target:
            self._freq = min(target, self._freq + delta)
        else:
            self._freq = max(target, self._freq - delta)
        if self._freq == 0 and not self._run:
            status = "Остановлен"
        elif self._freq < target:
            status = "Разгон"
        elif self._freq > target:
            status = "Торможение"
        else:
            status = "Работа"
        if status != self._status:
            self._status = status
            self.log("INFO", f"Состояние привода: {status}")

    def read(self) -> dict[str, Any]:
        self._step()
        return {
            "setpoint": self._setpoint,
            "freq": round(self._freq, 1),
            "current": round(0.3 + self._freq * 0.04, 2) if self._freq else 0.0,
            "run": self._run,
            "reverse": self._reverse,
            "status": self._status,
            "fault": False,
        }

    def apply(self, values: dict[str, Any]) -> None:
        if "setpoint" in values:
            self._setpoint = to_float(values["setpoint"], 0, MAX_FREQ, self._setpoint)
        if "run" in values:
            self._run = bool(values["run"])
        if "reverse" in values:
            self._reverse = bool(values["reverse"])
        self.log(
            "INFO",
            f"Команда: уставка {self._setpoint:g} Гц, "
            f"{'пуск' if self._run else 'стоп'}, {'реверс' if self._reverse else 'вперёд'}",
        )


device = Pchv3()
router = build_router(device)
