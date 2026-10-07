"""DataProvider: o motor não depende da origem dos dados."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from ..models.provenance import Provenance


@dataclass
class CalibrationTarget:
    """Alvos OBSERVÁVEIS (marginais da nota FINAL) contra os quais um modelo pode ser conferido.
    NÃO contém notas por avaliador — se essas existirem, usar RealDataProvider.rater_scores()."""

    comp_probs: np.ndarray           # (5, 11): P(nota final da competência = 0,20,...,200)
    comp_mean: np.ndarray            # (5,) em pontos
    total_mean: float
    total_std: float
    n_valid: int
    n_1000: Optional[int] = None
    p_zero: Optional[float] = None
    provenance: Provenance = Provenance.OBSERVADO
    source: str = ""
    extra: dict = field(default_factory=dict)


class DataProvider(ABC):
    name: str = "base"
    data_version: str = ""

    @abstractmethod
    def calibration_target(self) -> CalibrationTarget: ...

    def rater_scores(self):
        """Notas por avaliador (N,2,5) se existirem; por padrão não existem."""
        raise NotImplementedError("Este provedor não dispõe de notas por avaliador.")
