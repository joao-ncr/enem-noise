"""Experimentos Monte Carlo: grade de cenários e escalas (1, 10, 100, 1000 redações)."""
from __future__ import annotations

import itertools
from typing import Callable, Dict, Iterable, List, Sequence

import numpy as np

from ..models.competency import NoiseParams
from ..models.essay import Essay
from ..models.evaluator import Panel
from .engine import SimulationEngine


def run_grid(essays: Sequence[Essay], models: Sequence[str], panels: Sequence[str],
             sigmas: Sequence[float], sigma_us: Sequence[float], iterations: int, seed: int,
             cutoffs: Sequence[float] = (), rule: str = "inep_2025",
             sigma_beta: float = 0.2, progress: Callable[[str], None] = None) -> List[Dict]:
    """Executa a grade completa. Cada célula usa seed derivada de forma determinística."""
    rows = []
    cells = list(itertools.product(models, panels, sigmas, sigma_us, essays))
    for k, (m, pn, s, su, es) in enumerate(cells):
        params = NoiseParams.uniform(s, sigma_u=su, sigma_beta=sigma_beta)
        eng = SimulationEngine(m, rule, params, Panel.preset(pn))
        cell_seed = int(np.random.SeedSequence([seed, k]).generate_state(1)[0])
        res = eng.run_essay(es, iterations, cell_seed, cutoffs)
        rows.append({"cell": k, "model": m, "panel": pn, "sigma": s, "sigma_u": su, "essay": es.id,
                     "latent_total": res.latent_total, "seed": cell_seed, "stats": res.statistics,
                     "provenance": res.provenance})
        if progress:
            progress(f"{k + 1}/{len(cells)}")
    return rows
