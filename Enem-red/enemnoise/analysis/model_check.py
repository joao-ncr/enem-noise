"""Sensibilidade à escolha de modelo: compara conclusões entre modelos de erro (M0, M1, M1H).

Se as conclusões mudam de um modelo para outro, isso é um RESULTADO (a conclusão depende de uma hipótese),
não um incômodo. Retorna alerta quando a divergência relativa passa da tolerância.
"""
from __future__ import annotations

from typing import Sequence

from ..models.competency import NoiseParams
from ..models.essay import Essay
from ..models.evaluator import Panel
from ..simulation.engine import SimulationEngine


def model_divergence(essay: Essay, params: NoiseParams, panel: Panel, models: Sequence[str] = ("M0", "M1", "M1H"),
                     iterations: int = 20_000, seed: int = 1, rule: str = "inep_2025", tol: float = 0.25) -> dict:
    rows = {}
    for m in models:
        st = SimulationEngine(m, rule, params, panel).run_essay(essay, iterations, seed).statistics
        rows[m] = {"std": st["std"], "p_third": st["p_third_rater"], "p_dev40": st["noise_only"]["p_abs_dev_ge_threshold"]}
    ref = models[0]
    alerts = []
    for m in models[1:]:
        for k in ("std", "p_third", "p_dev40"):
            a, b = rows[ref][k], rows[m][k]
            rel = abs(b - a) / max(abs(a), 1e-9)
            if rel > tol:
                alerts.append({"metric": k, "models": [ref, m], "relative_diff": rel})
    return {"by_model": rows, "alerts": alerts, "tolerance": tol,
            "message": "Conclusões dependem do modelo de erro." if alerts else "Conclusões estáveis entre modelos."}
