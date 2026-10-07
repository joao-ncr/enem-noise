from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...models.evaluator import panel_names
from ...registry import RunRegistry
from ...simulation.distributions import MODELS
from ...simulation.scoring import RULES
from ..controllers import runs, scenario as scn
from ..schemas.models import CompareRequest, ScenarioRequest, SensitivityRequest, SimulateRequest

router = APIRouter()


def _run(endpoint: str, req_model):
    req = req_model.model_dump()
    persist = req.pop("persist", True)
    try:
        return runs.execute(endpoint, req, persist)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/simulate", tags=["simulação"])
def simulate(req: SimulateRequest):
    return _run("simulate", req)


@router.post("/compare", tags=["simulação"])
def compare(req: CompareRequest):
    return _run("compare", req)


@router.post("/sensitivity", tags=["simulação"])
def sensitivity(req: SensitivityRequest):
    return _run("sensitivity", req)


@router.post("/scenario", tags=["simulação"])
def scenario(req: ScenarioRequest):
    return _run("scenario", req)


@router.get("/scenario", tags=["simulação"])
def list_scenarios():
    return scn.list_scenarios()


@router.get("/meta", tags=["meta"])
def meta():
    return {"models": {k: m.card.name for k, m in MODELS.items()}, "scoring_rules": {k: r.description for k, r in RULES.items()},
            "panels": panel_names(),
            "provenance_levels": ["OBSERVADO", "ESTIMADO", "SIMULADO", "HIPOTÉTICO"]}


@router.get("/runs", tags=["reprodutibilidade"])
def list_runs():
    return RunRegistry().list()


@router.get("/runs/{run_id}", tags=["reprodutibilidade"])
def get_run(run_id: str):
    try:
        return {"manifest": RunRegistry().load(run_id), "result": RunRegistry().load_result(run_id)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="run não encontrado")


@router.post("/runs/{run_id}/replay", tags=["reprodutibilidade"])
def replay(run_id: str):
    try:
        return runs.replay(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="run não encontrado")
