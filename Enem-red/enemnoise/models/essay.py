"""Redação: desempenho latente por competência (em níveis 0..5)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .competency import N_COMP, MAX_LEVEL, STEP
from .provenance import Provenance


def latent_total(theta) -> np.ndarray:
    """Nota latente de referência T* = 40 * soma(clip(theta, 0, 5)). Definição DO MODELO (não observável)."""
    th = np.clip(np.asarray(theta, dtype=float), 0, MAX_LEVEL)
    return STEP * th.sum(axis=-1)


@dataclass(frozen=True)
class Essay:
    id: str
    theta: tuple
    provenance: Provenance = Provenance.HIPOTETICO
    note: str = ""

    def __post_init__(self):
        th = tuple(float(x) for x in self.theta)
        if len(th) != N_COMP:
            raise ValueError(f"theta precisa ter {N_COMP} valores (níveis por competência)")
        object.__setattr__(self, "theta", th)

    @property
    def theta_array(self) -> np.ndarray:
        return np.asarray(self.theta, dtype=float)

    @property
    def latent_total(self) -> float:
        return float(latent_total(self.theta_array))

    @classmethod
    def from_points(cls, id: str, points: Sequence[float], **kw) -> "Essay":
        return cls(id, tuple(float(p) / STEP for p in points), **kw)

    @classmethod
    def uniform(cls, id: str, level: float, **kw) -> "Essay":
        return cls(id, (level,) * N_COMP, **kw)

    def with_delta(self, deltas: dict, id: str = None) -> "Essay":
        """deltas: {indice_competencia(0..4): delta em níveis}"""
        th = list(self.theta)
        for k, v in deltas.items():
            th[int(k)] += float(v)
        return Essay(id or self.id + "+", tuple(th), self.provenance, self.note)

    def to_dict(self) -> dict:
        return {"id": self.id, "theta": list(self.theta), "provenance": self.provenance.name}
