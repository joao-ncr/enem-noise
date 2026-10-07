"""Comparação de redações: P(A>B), P(empate), P(inversão), sobreposição."""
from __future__ import annotations

from typing import Sequence

import numpy as np

from ..models.essay import Essay
from ..simulation.engine import SimulationEngine
from ..simulation.summary import to_jsonable


def overlap_coefficient(fa: np.ndarray, fb: np.ndarray, step: float = 20.0) -> float:
    """Σ min(pA, pB) sobre bins de largura `step` (1 = distribuições idênticas, 0 = disjuntas)."""
    lo = min(fa.min(), fb.min()); hi = max(fa.max(), fb.max())
    edges = np.arange(np.floor(lo / step) * step - step / 2, hi + step, step)
    pa, _ = np.histogram(fa, bins=edges); pb, _ = np.histogram(fb, bins=edges)
    return float(np.minimum(pa / fa.size, pb / fb.size).sum())


def compare_pair(engine: SimulationEngine, a: Essay, b: Essay, iterations: int, seed: int) -> dict:
    """As duas redações são corrigidas por pares de avaliadores INDEPENDENTES (seeds distintas)."""
    sa, sb = [int(x) for x in np.random.SeedSequence(seed).generate_state(2)]
    ra = engine.run_essay(a, iterations, sa)
    rb = engine.run_essay(b, iterations, sb)
    fa, fb = ra.final, rb.final
    ta, tb = a.latent_total, b.latent_total
    p_gt, p_lt, p_eq = float((fa > fb).mean()), float((fa < fb).mean()), float((fa == fb).mean())
    diff = fa - fb
    se = float(diff.std(ddof=1) / np.sqrt(diff.size))
    out = {
        "a": a.id, "b": b.id, "latent_total_a": ta, "latent_total_b": tb, "latent_diff": ta - tb,
        "mean_a": float(fa.mean()), "mean_b": float(fb.mean()),
        "mean_diff": float(diff.mean()), "ci95_mean_diff": [float(diff.mean() - 1.96 * se), float(diff.mean() + 1.96 * se)],
        "std_a": float(fa.std(ddof=1)), "std_b": float(fb.std(ddof=1)),
        "overlap_coefficient": overlap_coefficient(fa, fb),
        "p_a_gt_b": p_gt, "p_b_gt_a": p_lt, "p_tie": p_eq,
        "provenance": ra.provenance,
    }
    if ta != tb:
        hi_is_a = ta > tb
        out["p_ranking_inversion"] = p_lt if hi_is_a else p_gt   # inverte a ordem latente
        out["p_tie_or_inversion"] = out["p_ranking_inversion"] + p_eq
        out["latent_order"] = "A>B" if hi_is_a else "B>A"
    else:
        out["p_ranking_inversion"] = None
        out["note"] = "Latentes iguais: não há ordem 'verdadeira' para inverter."
    return to_jsonable(out)


def compare_many(engine: SimulationEngine, essays: Sequence[Essay], iterations: int, seed: int) -> dict:
    pairs = []
    k = 0
    for i in range(len(essays)):
        for j in range(i + 1, len(essays)):
            pseed = int(np.random.SeedSequence([seed, k]).generate_state(1)[0]); k += 1
            pairs.append(compare_pair(engine, essays[i], essays[j], iterations, pseed))
    return {"pairs": pairs}
