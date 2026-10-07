"""Cenários nomeados: presets sobre /simulate e /compare."""
from __future__ import annotations

from . import simulation as sim

BASE_PARAMS = {"sigma": 0.35, "sigma_u": 0.15, "sigma_beta": 0.1}

SCENARIOS = {
    "avaliador_rigoroso": {"kind": "simulate", "desc": "Painel só de avaliadores rigorosos (beta=-0,3).",
                           "req": {"essay_profile": {"id": "r", "theta": [3.5] * 5}, "evaluator_profile": {"preset": "rigoroso"},
                                   "cutoffs": [600, 700]}},
    "avaliador_permissivo": {"kind": "simulate", "desc": "Painel só de avaliadores permissivos (beta=+0,3).",
                             "req": {"essay_profile": {"id": "r", "theta": [3.5] * 5}, "evaluator_profile": {"preset": "permissivo"},
                                     "cutoffs": [600, 700]}},
    "painel_misto": {"kind": "simulate", "desc": "Metade rigorosos, metade permissivos: sorteio do par importa.",
                     "req": {"essay_profile": {"id": "r", "theta": [3.5] * 5}, "evaluator_profile": {"preset": "misto"},
                             "cutoffs": [600, 700]}},
    "alta_variabilidade": {"kind": "simulate", "desc": "Avaliadores com ruído 1,6x.",
                           "req": {"essay_profile": {"id": "r", "theta": [3.5] * 5}, "evaluator_profile": {"preset": "alta_variabilidade"},
                                   "cutoffs": [600, 700]}},
    "baixa_variabilidade": {"kind": "simulate", "desc": "Avaliadores com ruído 0,6x.",
                            "req": {"essay_profile": {"id": "r", "theta": [3.5] * 5}, "evaluator_profile": {"preset": "baixa_variabilidade"},
                                    "cutoffs": [600, 700]}},
    "fronteira_classificatoria": {"kind": "simulate", "desc": "Redação com T* exatamente no corte de 700.",
                                  "req": {"essay_profile": {"id": "f", "points": [140, 140, 140, 140, 140]},
                                          "cutoffs": [660, 700, 740]}},
    "notas_proximas": {"kind": "compare", "desc": "Duas redações a 40 pontos de distância (1 nível em 1 competência).",
                       "req": {"essays": [{"id": "A", "theta": [4, 4, 4, 4, 4]}, {"id": "B", "theta": [4, 4, 3, 4, 4]}]}},
    "desempenhos_distantes": {"kind": "compare", "desc": "Redações a 200 pontos de distância (controle).",
                              "req": {"essays": [{"id": "A", "theta": [4, 4, 4, 4, 4]}, {"id": "B", "theta": [3, 3, 3, 3, 3]}]}},
}


def list_scenarios() -> dict:
    return {k: v["desc"] for k, v in SCENARIOS.items()}


def scenario(req: dict) -> dict:
    name = req["name"]
    if name not in SCENARIOS:
        raise ValueError(f"cenário desconhecido: {name}. Opções: {sorted(SCENARIOS)}")
    spec = SCENARIOS[name]
    full = {"model": "M1", "scoring_rule": "inep_2025", "parameters": dict(BASE_PARAMS), "evaluator_profile": {"preset": "neutro"},
            "iterations": req["iterations"], "seed": req["seed"], **spec["req"]}
    out = sim.simulate(full) if spec["kind"] == "simulate" else sim.compare(full)
    out["scenario"] = {"name": name, "description": spec["desc"]}
    return out
