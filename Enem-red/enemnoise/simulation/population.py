"""População HIPOTÉTICA de redações (theta latente). Substituível por dado real via DataProvider."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..models.provenance import Provenance


@dataclass(frozen=True)
class PopulationPrior:
    mu: tuple = (3.2, 3.2, 3.0, 3.0, 3.0)   # médias latentes por competência (níveis)
    tau: float = 0.9                        # desvio entre redações
    rho: float = 0.7                        # correlação entre competências (fator geral)
    provenance: Provenance = Provenance.HIPOTETICO

    def sample(self, rng: np.random.Generator, m: int) -> np.ndarray:
        g = rng.normal(size=(m, 1))
        z = rng.normal(size=(m, len(self.mu)))
        th = np.asarray(self.mu)[None, :] + self.tau * (np.sqrt(self.rho) * g + np.sqrt(1 - self.rho) * z)
        # reflexão nos limites [0,5] (evita átomos em 0 e 5)
        th = np.where(th > 5, 10 - th, th)
        th = np.where(th < 0, -th, th)
        return np.clip(th, 0, 5)
