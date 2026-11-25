"""КИП: ТРМ138 — 8-канальный измеритель-регулятор (Modbus RTU).

Разработчик: Нестор В. В. (ветка ``feature/trm138``).
"""
from __future__ import annotations

import math
import random
import time
from typing import Any

from app.core.base import BaseDevice, to_float
from app.core.routing import build_router

CHANNELS = 8
 

class Trm138(BaseDevice):
    """Измеритель-регулятор ТРМ138: 8 входов температуры и 8 выходов."""

    slug = "trm138"
    title = "ТРМ138"
    model = "ТРМ138"
    description = "8-канальный измеритель-регулятор температуры"
    template = "trm138.html"
    image = "/static/img/trm138.svg"

    def __init__(self) -> None:
        super().__init__()
        self._sp = [40.0 + 5 * i for i in range(CHANNELS)]
        self._t0 = time.monotonic()
        self._alarm = [False] * CHANNELS

    def _simulate_pv(self, n: int) -> float:
        t = time.monotonic() - self._t0
        base = 38.0 + 5 * n
        return base + 4 * math.sin(t / 15 + n) + random.uniform(-0.2, 0.2)

    def read(self) -> dict[str, Any]:
        channels = []
        for n in range(CHANNELS):
            pv = self._simulate_pv(n)
            sp = self._sp[n]
            deviation = pv - sp
            alarm = abs(deviation) > 8
            if alarm != self._alarm[n]:
                self._alarm[n] = alarm
                if alarm:
                    self.log("WARN", f"Канал {n + 1}: отклонение {deviation:+.1f} °C")
                else:
                    self.log("INFO", f"Канал {n + 1}: возврат в норму")
            channels.append(
                {
                    "n": n + 1,
                    "pv": round(pv, 1),
                    "sp": sp,
                    "out": pv < sp,
                    "alarm": alarm,
                    "status": "Отклонение" if alarm else "Норма",
                }
            )
        return {"channels": channels, "alarms": sum(self._alarm)}

    def apply(self, values: dict[str, Any]) -> None:
        for n in range(CHANNELS):
            key = f"sp{n + 1}"
            if key in values:
                self._sp[n] = to_float(values[key], -50, 1000, self._sp[n])
        self.log("INFO", "Записаны уставки каналов")


device = Trm138()
router = build_router(device)
