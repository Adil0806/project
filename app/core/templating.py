"""Общий экземпляр Jinja2-шаблонизатора."""
from fastapi.templating import Jinja2Templates

from app import config

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
templates.env.globals["author"] = config.AUTHOR
templates.env.globals["refresh_ms"] = config.REFRESH_MS
