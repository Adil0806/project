"""Базовый класс прибора.

Каждый прибор наследуется от :class:`BaseDevice` и реализует три метода:
``read``, ``apply`` и (опционально) ``poll``. Благодаря этому единая фабрика
маршрутов :func:`app.core.routing.build_router` умеет обслуживать любой прибор.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any


def to_float(value: Any, lo: float, hi: float, default: float) -> float:
    """Преобразовать значение к float и ограничить диапазоном ``[lo, hi]``.

    :param value: исходное значение (строка из формы, число и т. д.)
    :param lo: нижняя граница
    :param hi: верхняя граница
    :param default: значение, если преобразование невозможно
    """
    try:
        number = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, number))


class BaseDevice:
    """Абстрактный промышленный прибор.

    Атрибуты класса описывают прибор в интерфейсе, методы — обмен данными.
    """

    slug: str = ""
    title: str = ""
    model: str = ""
    protocol: str = "Modbus RTU"
    description: str = ""
    template: str = ""
    image: str = ""
    #: Имена чекбоксов формы: если в форме их нет — значит сняты (False).
    flags: tuple[str, ...] = ()

    def __init__(self) -> None:
        self._log: deque[dict[str, str]] = deque(maxlen=500)
        self.log("INFO", "Успешное подключение к устройству (симуляция)")

    # ---- журнал ---------------------------------------------------------
    def log(self, level: str, message: str) -> None:
        """Добавить запись в журнал статусов (``INFO``/``WARN``/``ERROR``)."""
        self._log.appendleft(
            {"time": datetime.now().strftime("%H:%M:%S"), "level": level, "message": message}
        )

    def logs(self, limit: int = 10) -> list[dict[str, str]]:
        """Вернуть ``limit`` последних записей журнала (новые сверху)."""
        return list(self._log)[: max(1, limit)]

    # ---- обмен с прибором ----------------------------------------------
    def read(self) -> dict[str, Any]:
        """Прочитать текущее состояние прибора."""
        raise NotImplementedError

    def apply(self, values: dict[str, Any]) -> None:
        """Записать в прибор значения (уставки, команды)."""
        raise NotImplementedError

    def poll(self) -> dict[str, Any]:
        """Принудительный опрос прибора (кнопка «Опросить устройство»)."""
        state = self.read()
        self.log("INFO", "Опрос устройства выполнен")
        return state

    def info(self) -> dict[str, str]:
        """Краткое описание прибора для списков и API."""
        return {
            "slug": self.slug,
            "title": self.title,
            "model": self.model,
            "protocol": self.protocol,
            "description": self.description,
        }
