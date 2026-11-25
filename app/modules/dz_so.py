"""Датчик: ДЗ-СО — датчик загазованности по угарному газу (Modbus RTU).

Разработчик: Аллагулов А. Р. (ветка ``feature/dz-so``).
"""
from __future__ import annotations

import math
import random
import time
from typing import Any

from app.core.base import BaseDevice, to_float
from app.core.routing import build_router

LEVELS = ["Норма", "Порог 1", "Порог 2"]


class DzSo(BaseDevice):
    """Датчик СО: концентрация, два порога, два реле."""

    slug = "dz-so"
    title = "ДЗ-СО"
    model = "ДЗ-СО"
    description = "Датчик загазованности по угарному газу (CO)"
    template = "dz_so.html"
    image = "/static/img/dz-so.svg"

    def __init__(self) -> None:
        super().__init__()
        self._thr = [20.0, 50.0]
        self._t0 = time.monotonic()
        self._level = 0

    def read(self) -> dict[str, Any]:
        t = time.monotonic() - self._t0
        conc = 8 + 6 * math.sin(t / 15) + random.uniform(-0.5, 0.5)
        if (t % 120) > 95:  # периодический всплеск концентрации
            conc += 50
        conc = max(0.0, conc)
        level = 2 if conc >= self._thr[1] else 1 if conc >= self._thr[0] else 0
        if level != self._level:
            self.log("WARN" if level else "INFO", f"Состояние: {LEVELS[level]} ({conc:.1f} мг/м³)")
            self._level = level
        return {
            "concentration": round(conc, 1),
            "unit": "мг/м³",
            "thr1": self._thr[0],
            "thr2": self._thr[1],
            "level": level,
            "status": LEVELS[level],
            "relay1": level >= 1,
            "relay2": level >= 2,
        }

    def apply(self, values: dict[str, Any]) -> None:
        thr1 = to_float(values.get("thr1"), 0, 500, self._thr[0])
        thr2 = to_float(values.get("thr2"), 0, 500, self._thr[1])
        if thr2 <= thr1:
            self.log("ERROR", "Порог 2 должен быть больше порога 1 — значения не записаны")
            return
        self._thr = [thr1, thr2]
        self.log("INFO", f"Записаны пороги: {thr1:g} / {thr2:g} мг/м³")


device = DzSo()
router = build_router(device)
