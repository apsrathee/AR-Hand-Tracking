"""
utils/config.py
Loads config.json exactly once at startup and shares it across all modules.
Import CFG anywhere you need a config value — no repeated file reads.
"""
import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

with open(_CONFIG_PATH) as _f:
    CFG: dict = json.load(_f)
