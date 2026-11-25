"""Конфигурация Sphinx: документация собирается из docstring (autodoc)."""
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "SCADA — команда 4"
author = "Команда 4"
language = "ru"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx.ext.napoleon"]
html_theme = "sphinx_rtd_theme"
autodoc_member_order = "bysource"
