"""SimulationEngine: motor puro (sem I/O). Entrada: configuração; saída: notas.

Reprodutibilidade: a simulação é dividida em blocos de CHUNK linhas; o bloco i usa
default_rng(SeedSequence(seed, spawn_key=(i,))). O resultado só depende de (seed, parâmetros, CHUNK).
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from ..models.competency import NoiseParams
from ..models.essay import Essay, latent_total
from ..models.evaluator import Panel
from ..models.provenance import result_label, Provenance
from ..models.result import GradeBatch, SimulationResult
from .distributions import get_model
from .evaluator import RaterSampler
from .scoring import consolidate, get_rule
from .summary import summarize

CHUNK = 100_000


class SimulationEngine:
    def __init__(self, model: str = "M1", rule: str = "inep_2025",
                 params: Optional[NoiseParams] = None, panel: Optional[Panel] = None):
        self.model_key, self.rule_key = model, rule
        self.model = get_model(model)
        self.rule = get_rule(rule)
        self.params = params or NoiseParams()
        self.panel = panel or Panel.preset("neutro")
        self.sampler = RaterSampler(self.panel, self.params)

    # ---- núcleo --------------------------------------------------------------------------
    def _observe(self, theta: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        beta, kappa, shrink = self.sampler.sample(rng, theta.shape[0])
        return self.model.observe(theta, rng, beta, kappa, shrink, self.params)

    def grade(self, theta: np.ndarray, rng: np.random.Generator) -> GradeBatch:
        """Cada linha de theta (N,5) recebe uma correção completa (2 avaliadores [+3º] [+banca])."""
        s1 = self._observe(theta, rng)
        s2 = self._observe(theta, rng)

        def third_fn(idx):
            return self._observe(theta[idx], rng)

        def banca_fn(idx):
            return np.stack([self._observe(theta[idx], rng) for _ in range(3)], axis=1)

        fc, third, banca = consolidate(self.rule, s1, s2, third_fn, banca_fn)
        return GradeBatch(s1, s2, fc, third, banca)

    def grade_chunked(self, theta_rows: np.ndarray, seed: int) -> GradeBatch:
        theta_rows = np.asarray(theta_rows, dtype=float)
        parts = []
        for i, start in enumerate(range(0, theta_rows.shape[0], CHUNK)):
            rng = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(i,)))
            parts.append(self.grade(theta_rows[start:start + CHUNK], rng))
        return GradeBatch.concat(parts)

    # ---- uma redação, N avaliações ---------------------------------------------------------
    def run_essay(self, essay: Essay, iterations: int, seed: int,
                  cutoffs: Sequence[float] = (), keep_batch: bool = True) -> SimulationResult:
        theta = np.broadcast_to(essay.theta_array, (iterations, essay.theta_array.size))
        batch = self.grade_chunked(theta, seed)
        t_star = float(latent_total(essay.theta_array))
        stats = summarize(batch, t_star, cutoffs)
        label = result_label([essay.provenance, self.params.provenance,
                              *[p.provenance for p in self.panel.profiles]])
        return SimulationResult(essay.id, batch, t_star, stats, label,
                                {"model": self.model_key, "rule": self.rule_key, "seed": seed,
                                 "iterations": iterations})
