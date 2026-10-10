#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Config - HF key loaded from environment (never commit real keys)."""
import os

try:
    from scripts.config_local import HF_API_KEY as _LOCAL_KEY
except Exception:
    try:
        from config_local import HF_API_KEY as _LOCAL_KEY
    except Exception:
        _LOCAL_KEY = ""

HF_API_KEY = os.getenv("HF_API_KEY", _LOCAL_KEY or "")
