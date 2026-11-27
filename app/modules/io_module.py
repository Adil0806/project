"""IO-модуль: МВ110-224.2А (2 аналоговых входа) + МУ110-224.6У (6 аналоговых выходов).

Разработчик: Бульц М. Б. (ветка ``feature/io-module``).
"""
from __future__ import annotations

import math
import time
from typing import Any

from app.core.base import BaseDevice, to_float
from app.core.routing import build_router

AI_COUNT = 2
AO_COUNT = 6
MA_MIN, MA_MAX = 4.0, 20.0


class IoModule(BaseDevice):
    """Связка модулей аналогового ввода и вывода (сигнал 4–20 мА)."""

    slug = "io"
    title = "МВ110-224.2А + МУ110-224.6У"
    model = "МВ110-224.2А + МУ110-224.6У"
    description = "Аналоговый ввод (2 канала) и вывод (6 каналов)"
    template = "io_module.html"
    image = "/static/img/io.svg"

    def __init__(self) -> None:
        super().__init__()
        self._ao = [MA_MIN] * AO_COUNT
        self._t0 = time.monotonic()

    def read(self) -> dict[str, Any]:
        t = time.monotonic() - self._t0
        ai = []
        for n in range(AI_COUNT):
            ma = 12 + 6 * math.sin(t / (10 + 5 * n) + n)
            percent = (ma - MA_MIN) / (MA_MAX - MA_MIN) * 100
            ai.append({"n": n + 1, "ma": round(ma, 2), "percent": round(percent, 1)})
        ao = [{"n": i + 1, "ma": v} for i, v in enumerate(self._ao)]
        return {"ai": ai, "ao": ao}

    def apply(self, values: dict[str, Any]) -> None:
        for i in range(AO_COUNT):
            key = f"ao{i + 1}"
            if key in values:
                self._ao[i] = to_float(values[key], MA_MIN, MA_MAX, self._ao[i])
        self.log("INFO", "Записаны значения аналоговых выходов")


device = IoModule()
router = build_router(device)

# IO-модуль: МВ110 (ввод) и МУ110 (вывод)
