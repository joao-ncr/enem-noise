"""Registro de execuções: seed, iterações, parâmetros, versões, timestamp, configuração, hash do resultado."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
from pathlib import Path
from typing import Any, Optional

import numpy as np

from . import MODEL_VERSION, DATA_VERSION_SIMULATED, __version__
from .simulation.summary import to_jsonable


def canonical(o: Any) -> str:
    return json.dumps(to_jsonable(o), sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_of(o: Any) -> str:
    return hashlib.sha256(canonical(o).encode("utf-8")).hexdigest()


def default_dir() -> Path:
    return Path(os.environ.get("ENEM_NOISE_DATA_DIR", "data/simulated"))


class RunRegistry:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base = Path(base_dir) if base_dir else default_dir()
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, endpoint: str, request: dict, result: dict, seed: int, iterations: int,
             data_version: str = DATA_VERSION_SIMULATED, scores: Optional[np.ndarray] = None) -> dict:
        cfg_hash = sha256_of({"endpoint": endpoint, "request": request})
        ts = dt.datetime.now(dt.timezone.utc)
        run_id = f"{ts.strftime('%Y%m%dT%H%M%S')}-{cfg_hash[:8]}"
        manifest = {
            "run_id": run_id, "timestamp_utc": ts.isoformat(), "endpoint": endpoint, "seed": seed,
            "iterations": iterations, "model_version": MODEL_VERSION, "package_version": __version__,
            "data_version": data_version, "config_hash": cfg_hash, "result_hash": sha256_of(result),
            "numpy": np.__version__, "python": platform.python_version(), "request": to_jsonable(request),
        }
        d = self.base / run_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (d / "result.json").write_text(canonical(result), encoding="utf-8")
        if scores is not None:
            np.savez_compressed(d / "scores.npz", final=np.asarray(scores, dtype=np.float32))
        return manifest

    def load(self, run_id: str) -> dict:
        p = self.base / run_id / "manifest.json"
        if not p.exists():
            raise FileNotFoundError(run_id)
        return json.loads(p.read_text(encoding="utf-8"))

    def load_result(self, run_id: str) -> dict:
        return json.loads((self.base / run_id / "result.json").read_text(encoding="utf-8"))

    def list(self) -> list:
        return sorted(p.name for p in self.base.iterdir() if (p / "manifest.json").exists())
