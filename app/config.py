"""Настройки приложения (берутся из переменных окружения)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

#: Режим симуляции: приборы не подключены, данные генерируются программно.
SIMULATION: bool = os.getenv("SCADA_SIMULATION", "1") == "1"

#: Параметры последовательного порта для Modbus RTU (используются при SIMULATION=0).
SERIAL_PORT: str = os.getenv("SCADA_SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUDRATE: int = int(os.getenv("SCADA_SERIAL_BAUDRATE", "9600"))

#: Период автообновления интерфейса, мс.
REFRESH_MS: int = int(os.getenv("SCADA_REFRESH_MS", "2000"))

AUTHOR = "Команда 4"
