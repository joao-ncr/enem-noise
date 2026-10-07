"""Sorteio de avaliadores de um painel."""
from __future__ import annotations

import numpy as np

from ..models.competency import NoiseParams
from ..models.evaluator import Panel


class RaterSampler:
    def __init__(self, panel: Panel, params: NoiseParams):
        self.panel, self.params = panel, params
        self._w = panel.weights

    def sample(self, rng: np.random.Generator, n: int):
        """Sorteia n avaliadores independentes -> (beta, kappa, shrink), cada um shape (n,)."""
        idx = rng.choice(len(self.panel.profiles), size=n, p=self._w)
        beta = self.panel.betas[idx] + rng.normal(0.0, self.params.sigma_beta, n)
        return beta, self.panel.kappas[idx], self.panel.shrinks[idx]
