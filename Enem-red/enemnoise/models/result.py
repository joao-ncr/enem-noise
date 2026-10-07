"""Estruturas de resultado."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class GradeBatch:
    """Resultado de corrigir N linhas (cada linha = uma redação submetida a uma correção completa)."""

    s1: np.ndarray            # (N,5) pontos do 1º avaliador
    s2: np.ndarray            # (N,5) pontos do 2º avaliador
    final_comp: np.ndarray    # (N,5) nota final por competência
    third: np.ndarray         # (N,) bool: terceiro corretor acionado
    banca: np.ndarray         # (N,) bool: banca acionada

    @property
    def final(self) -> np.ndarray:
        return self.final_comp.sum(axis=1)

    @classmethod
    def concat(cls, parts: list) -> "GradeBatch":
        return cls(*(np.concatenate([getattr(p, f) for p in parts]) for f in
                     ("s1", "s2", "final_comp", "third", "banca")))


@dataclass
class SimulationResult:
    essay_id: str
    batch: GradeBatch
    latent_total: float
    statistics: dict
    provenance: str
    meta: dict = field(default_factory=dict)

    @property
    def final(self) -> np.ndarray:
        return self.batch.final
