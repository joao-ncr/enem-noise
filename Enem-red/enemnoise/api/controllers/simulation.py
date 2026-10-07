"""Controladores: funções puras (request dict -> result dict). Determinísticas dado o seed."""
from __future__ import annotations

import numpy as np

from ...analysis.compare import compare_many
from ...analysis.paradox import ParadoxDetector
from ...analysis.sensitivity import sensitivity_latent
from ...simulation.summary import to_jsonable
from .common import build_engine, build_essay

DISCLAIMER = ("Resultado SIMULADO. Parâmetros HIPOTÉTICOS não são evidência empírica sobre o ENEM real. "
              "Interprete apenas como mapa condicional às premissas listadas no manifest.")


def simulate(req: dict) -> dict:
    eng = build_engine(req)
    essay = build_essay(req["essay_profile"])
    res = eng.run_essay(essay, req["iterations"], req["seed"], req.get("cutoffs", []))
    st = res.statistics
    out = {
        "provenance": res.provenance, "disclaimer": DISCLAIMER,
        "essay": essay.to_dict(), "latent_total": res.latent_total,
        "distribution": st["distribution"],
        "statistics": {k: v for k, v in st.items() if k not in ("distribution", "classification_impact")},
        "classification_impact": st["classification_impact"],
        "paradoxes": [f.to_dict() for f in ParadoxDetector().scan(
            stats=st, cutoffs=req.get("cutoffs", []))],
    }
    n = req.get("return_scores", 0)
    if n:
        out["scores"] = res.final[:n].tolist()
    return to_jsonable(out)


def compare(req: dict) -> dict:
    eng = build_engine(req)
    essays = [build_essay(e) for e in req["essays"]]
    out = compare_many(eng, essays, req["iterations"], req["seed"])
    det = ParadoxDetector()
    for p in out["pairs"]:
        p["paradoxes"] = [det.inversion(p).to_dict(), det.overlap(p).to_dict()]
    out["disclaimer"] = DISCLAIMER
    return to_jsonable(out)


def sensitivity(req: dict) -> dict:
    eng = build_engine(req)
    essay = build_essay(req["essay_profile"])
    out = sensitivity_latent(eng, essay, req["perturbations"], req["iterations"], req["seed"], req.get("cutoffs", []))
    det = ParadoxDetector()
    out["paradoxes"] = [det.small_change_big_consequence(out).to_dict(), det.nonproportionality(out).to_dict()]
    out["disclaimer"] = DISCLAIMER
    return to_jsonable(out)
