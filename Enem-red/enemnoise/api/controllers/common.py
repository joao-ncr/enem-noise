from __future__ import annotations

from ...models.competency import NoiseParams
from ...models.essay import Essay
from ...models.evaluator import Panel
from ...models.provenance import Provenance
from ...simulation.engine import SimulationEngine


def build_essay(d: dict) -> Essay:
    if d.get("theta") is not None:
        return Essay(d.get("id", "essay"), tuple(d["theta"]))
    return Essay.from_points(d.get("id", "essay"), d["points"])


def build_panel(d: dict) -> Panel:
    if d.get("preset"):
        return Panel.preset(d["preset"])
    return Panel.from_dict({"profiles": d["profiles"], "name": d.get("name", "custom")})


def build_params(d: dict) -> NoiseParams:
    sc = d.get("sigma_c")
    if sc is None:
        sc = [d["sigma"] if d.get("sigma") is not None else 0.35] * 5
    return NoiseParams(tuple(sc), d.get("sigma_u", 0.15), d.get("sigma_beta", 0.1), d.get("het_slope", 0.8),
                       Provenance.HIPOTETICO)


def build_engine(req: dict) -> SimulationEngine:
    return SimulationEngine(req.get("model", "M1"), req.get("scoring_rule", "inep_2025"),
                            build_params(req.get("parameters", {})), build_panel(req.get("evaluator_profile", {"preset": "neutro"})))
