"""Provedor SIMULADO: tudo é HIPOTÉTICO."""
from __future__ import annotations

import numpy as np

from .. import DATA_VERSION_SIMULATED
from ..models.competency import NoiseParams
from ..models.evaluator import Panel
from ..models.provenance import Provenance
from ..simulation.engine import SimulationEngine
from ..simulation.population import PopulationPrior
from .base import CalibrationTarget, DataProvider


def target_from_finals(final_comp: np.ndarray, source: str, provenance: Provenance,
                       n_1000=None, p_zero=None) -> CalibrationTarget:
    fc = np.asarray(final_comp, float)
    grid = np.round(fc / 20.0).astype(int).clip(0, 10)
    probs = np.stack([np.bincount(grid[:, c], minlength=11) / fc.shape[0] for c in range(5)])
    tot = fc.sum(axis=1)
    return CalibrationTarget(probs, fc.mean(axis=0), float(tot.mean()), float(tot.std(ddof=1)), fc.shape[0],
                             n_1000, p_zero, provenance, source)


class SimulatedDataProvider(DataProvider):
    """Gera um alvo SINTÉTICO com sigma conhecido (útil para testar identificabilidade da calibração)."""

    name = "simulated"
    data_version = DATA_VERSION_SIMULATED

    def __init__(self, true_sigma: float = 0.35, n: int = 50_000, seed: int = 123,
                 prior: PopulationPrior = None, sigma_u: float = 0.15, model: str = "M1", panel: str = "neutro"):
        self.true_sigma, self.n, self.seed, self.sigma_u = true_sigma, n, seed, sigma_u
        self.model, self.panel = model, panel
        self.prior = prior or PopulationPrior()

    def calibration_target(self) -> CalibrationTarget:
        eng = SimulationEngine(self.model, "inep_2025", NoiseParams.uniform(self.true_sigma, sigma_u=self.sigma_u),
                               Panel.preset(self.panel))
        th = self.prior.sample(np.random.default_rng(self.seed), self.n)
        b = eng.grade_chunked(th, self.seed + 1)
        t = target_from_finals(b.final_comp, f"SINTÉTICO (sigma verdadeiro={self.true_sigma}, gerador={self.model}/{self.panel})", Provenance.SIMULADO)
        t.extra = {"true_sigma": self.true_sigma, "p_third": float(b.third.mean())}
        return t
