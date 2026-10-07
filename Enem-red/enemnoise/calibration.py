"""Filtro de CONSISTÊNCIA (não estimação) entre o modelo e alvos observáveis.

AVISO DE IDENTIFICABILIDADE: a distribuição marginal da nota FINAL mistura variância de desempenho (tau)
e variância de avaliação (sigma). Com o modelo CORRETAMENTE especificado (caso de um alvo sintético gerado pela
própria família do modelo) a marginal pode recuperar sigma; com dados reais a família é desconhecida, e outras
combinações (tau, sigma, estrutura de painel, heterocedasticidade) podem reproduzir marginais parecidas.
Por isso esta rotina é um FILTRO de consistência, não um estimador. O exp003 inclui um teste de má especificação.
Estimar sigma de forma robusta exige notas POR AVALIADOR (dupla correção) ou a taxa real de terceiro corretor.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

from .models.competency import NoiseParams
from .models.evaluator import Panel
from .providers.base import CalibrationTarget
from .providers.simulated import target_from_finals
from .simulation.engine import SimulationEngine
from .simulation.population import PopulationPrior
from .models.provenance import Provenance


def _w1_discrete(p: np.ndarray, q: np.ndarray, step: float = 20.0) -> float:
    return float(np.abs(np.cumsum(p) - np.cumsum(q)).sum() * step)


def _distance(sim_fc: np.ndarray, tgt: CalibrationTarget) -> float:
    simt = target_from_finals(sim_fc, "sim", Provenance.SIMULADO)
    d = sum(_w1_discrete(simt.comp_probs[c], tgt.comp_probs[c]) for c in range(5)) / 5.0
    d += abs(simt.total_std - tgt.total_std) / 5.0       # escala: 5 competências
    return float(d)


def fit_for_sigma(tgt: CalibrationTarget, sigma: float, sigma_u: float, n: int, seed: int,
                  taus=(0.5, 0.7, 0.9, 1.1, 1.3), rhos=(0.5, 0.7, 0.9), rule: str = "inep_2025",
                  model: str = "M1") -> Dict:
    eng = SimulationEngine(model, rule, NoiseParams.uniform(sigma, sigma_u=sigma_u), Panel.preset("neutro"))
    best = None
    for tau in taus:
        for rho in rhos:
            mu = np.clip(tgt.comp_mean / 40.0, 0.5, 4.5)
            for _ in range(3):                                # correção iterativa das médias
                prior = PopulationPrior(tuple(mu), tau, rho)
                th = prior.sample(np.random.default_rng(seed), n)
                b = eng.grade_chunked(th, seed + 1)
                mu = np.clip(mu + (tgt.comp_mean - b.final_comp.mean(axis=0)) / 40.0, 0.2, 4.8)
            prior = PopulationPrior(tuple(mu), tau, rho)
            th = prior.sample(np.random.default_rng(seed), n)
            b = eng.grade_chunked(th, seed + 1)
            d = _distance(b.final_comp, tgt)
            if best is None or d < best["distance"]:
                best = {"sigma": sigma, "sigma_u": sigma_u, "tau": tau, "rho": rho, "mu": mu.tolist(),
                        "distance": d, "p_third": float(b.third.mean()), "p_banca": float(b.banca.mean()),
                        "sim_total_std": float(b.final.std(ddof=1))}
    return best


def consistency_scan(tgt: CalibrationTarget, sigmas: Sequence[float], sigma_u: float = 0.15, n: int = 20_000,
                     seed: int = 11, tolerance: float = 0.25, **kw) -> Dict:
    fits: List[Dict] = [fit_for_sigma(tgt, s, sigma_u, n, seed, **kw) for s in sigmas]
    dmin = min(f["distance"] for f in fits)
    for f in fits:
        f["consistent"] = f["distance"] <= dmin * (1 + tolerance) + 1e-9
    consistent = [f["sigma"] for f in fits if f["consistent"]]
    spread = (max(f["distance"] for f in fits) - dmin) / max(dmin, 1e-9)
    return {"fits": fits, "best_sigma": min(fits, key=lambda f: f["distance"])["sigma"],
            "consistent_sigmas": consistent, "relative_spread": spread,
            "narrow_consistent_set": bool(len(consistent) <= max(1, len(sigmas) // 3)),
            "warning": ("Faixa ampla de sigma é consistente com o alvo: a marginal NÃO identifica o ruído de "
                        "avaliação. Use notas por avaliador ou a taxa real de terceiro corretor.")
            if len(consistent) > max(1, len(sigmas) // 3) else
            "Faixa estreita de sigma consistente SOB ESTE MODELO (vale só se a especificação estiver correta; confira com a taxa real de terceiro corretor e com o teste de má especificação).",
            "target_source": tgt.source, "target_provenance": tgt.provenance.name}
