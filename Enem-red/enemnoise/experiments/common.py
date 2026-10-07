from __future__ import annotations

import datetime as dt
import json
import platform
from pathlib import Path

import numpy as np

from .. import MODEL_VERSION, DATA_VERSION_SIMULATED
from ..registry import sha256_of
from ..simulation.summary import to_jsonable


def make_manifest(name: str, config: dict, seed: int, iterations: int, data_version: str = DATA_VERSION_SIMULATED,
                  **extra) -> dict:
    return {"experiment": name, "seed": seed, "iterations": iterations, "model_version": MODEL_VERSION,
            "data_version": data_version, "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "config_hash": sha256_of(config), "numpy": np.__version__, "python": platform.python_version(),
            "config": to_jsonable(config), **extra}


def write_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(to_jsonable(obj), ensure_ascii=False, indent=2), encoding="utf-8")


def prepare(outdir) -> Path:
    p = Path(outdir)
    (p / "figures").mkdir(parents=True, exist_ok=True)
    return p
