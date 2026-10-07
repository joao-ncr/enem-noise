"""Análise de sensibilidade: Δ avaliação → Δ nota → Δ ranking → Δ decisão.

Dois espaços de perturbação (não confundir):
  * LATENTE:  muda o texto (theta); mede a resposta do sistema inteiro (com ruído).
  * OBSERVADO: muda a nota dada por UM avaliador a UMA competência (mudança de julgamento).
Usa números aleatórios comuns (mesma seed) para reduzir variância na comparação base x perturbado.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

from ..models.competency import STEP
from ..models.essay import Essay
from ..simulation.engine import SimulationEngine
from ..simulation.population import PopulationPrior
from ..simulation.scoring import consolidate
from ..simulation.summary import to_jsonable


def population_reference(engine: SimulationEngine, seed: int, m: int = 20_000,
                         prior: Optional[PopulationPrior] = None) -> np.ndarray:
    """Distribuição de notas finais de uma população HIPOTÉTICA (base para percentis)."""
    prior = prior or PopulationPrior()
    th = prior.sample(np.random.default_rng(seed), m)
    return np.sort(engine.grade_chunked(th, seed + 1).final)


def percentile_in(ref_sorted: np.ndarray, value: float) -> float:
    return float(np.searchsorted(ref_sorted, value, side="right") / ref_sorted.size * 100)


def sensitivity_latent(engine: SimulationEngine, essay: Essay, perturbations: Sequence[Dict],
                       iterations: int, seed: int, cutoffs: Sequence[float] = (),
                       ref_sorted: Optional[np.ndarray] = None) -> dict:
    """perturbations: lista de {competência(0..4): Δ em níveis}. Ex.: [{"2": 0.5}]  (0,5 nível = 20 pts)."""
    if ref_sorted is None:
        ref_sorted = population_reference(engine, seed + 7)
    base = engine.run_essay(essay, iterations, seed, cutoffs)
    rows = []
    for k, pert in enumerate(perturbations):
        e2 = essay.with_delta(pert, id=f"{essay.id}#p{k}")
        r2 = engine.run_essay(e2, iterations, seed, cutoffs)       # mesma seed = ruído comum
        dpts = e2.latent_total - essay.latent_total
        row = {"perturbation": {str(a): b for a, b in pert.items()}, "delta_latent_points": dpts,
               "delta_mean_final": r2.statistics["mean"] - base.statistics["mean"],
               "mean_base": base.statistics["mean"], "mean_perturbed": r2.statistics["mean"],
               "percentile_base": percentile_in(ref_sorted, base.statistics["mean"]),
               "percentile_perturbed": percentile_in(ref_sorted, r2.statistics["mean"]),
               "delta_p_third": r2.statistics["p_third_rater"] - base.statistics["p_third_rater"],
               "delta_p_cutoff": {}}
        row["delta_percentile"] = row["percentile_perturbed"] - row["percentile_base"]
        for c in cutoffs:
            row["delta_p_cutoff"][str(c)] = (r2.statistics["classification_impact"][str(c)]["p_ge"]
                                             - base.statistics["classification_impact"][str(c)]["p_ge"])
        rows.append(row)
    return to_jsonable({"essay": essay.id, "base": {"mean": base.statistics["mean"], "std": base.statistics["std"]},
                        "rows": rows, "provenance": base.provenance, "space": "latente"})


def observed_perturbation(engine: SimulationEngine, s1: np.ndarray, s2: np.ndarray, rater: int,
                          competency: int, delta_points: float, seed: int = 0) -> dict:
    """Muda a nota de UM avaliador em UMA competência (s1, s2: vetores (5,) de pontos). A mudança mínima real
    é de 40 pontos (um nível). Mostra Δ nota final e se a regra de discrepância/terceiro corretor mudou."""
    a = np.array([s1, s2], dtype=float)
    b = a.copy()
    b[rater, competency] = np.clip(b[rater, competency] + delta_points, 0, 200)

    def run(x):
        rng = np.random.default_rng(seed)
        theta_ref = x.mean(axis=0, keepdims=True) / STEP
        fc, third, banca = consolidate(engine.rule, x[0:1], x[1:2],
                                       lambda idx: engine._observe(theta_ref[idx * 0], rng),
                                       lambda idx: np.stack([engine._observe(theta_ref[idx * 0], rng) for _ in range(3)], axis=1))
        return float(fc.sum()), bool(third[0]), bool(banca[0])

    f0, t0, b0 = run(a)
    f1, t1, b1 = run(b)
    return to_jsonable({"final_before": f0, "final_after": f1, "delta_final": f1 - f0,
                        "third_before": t0, "third_after": t1, "banca_before": b0, "banca_after": b1,
                        "delta_input_points": float(b[rater, competency] - a[rater, competency]),
                        "note": "Se terceiro corretor é acionado, a nota final depende de nova avaliação sorteada."})


def competency_variability_heatmap(base_engine: SimulationEngine, essay: Essay, sigmas: Sequence[float],
                                   iterations: int, seed: int) -> dict:
    """Matriz competência x sigma: desvio-padrão da nota final ao variar só o sigma de UMA competência."""
    from ..simulation.engine import SimulationEngine as E
    data = np.zeros((5, len(sigmas)))
    for c in range(5):
        for j, s in enumerate(sigmas):
            eng = E(base_engine.model_key, base_engine.rule_key, base_engine.params.with_sigma(c, s), base_engine.panel)
            data[c, j] = eng.run_essay(essay, iterations, seed).statistics["std"]
    return {"sigmas": list(sigmas), "std_final": data}
