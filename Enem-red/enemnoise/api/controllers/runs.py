from __future__ import annotations

from ...registry import RunRegistry, sha256_of
from . import scenario as scn
from . import simulation as sim

DISPATCH = {"simulate": sim.simulate, "compare": sim.compare, "sensitivity": sim.sensitivity, "scenario": scn.scenario}


def execute(endpoint: str, req: dict, persist: bool = True, registry: RunRegistry = None) -> dict:
    result = DISPATCH[endpoint](req)
    if persist:
        reg = registry or RunRegistry()
        iters = req.get("iterations", 0)
        scores = None
        result["run_manifest"] = reg.save(endpoint, req, result, req.get("seed", 0), iters, scores=scores)
    return result


def replay(run_id: str, registry: RunRegistry = None) -> dict:
    reg = registry or RunRegistry()
    m = reg.load(run_id)
    req = m["request"]
    result = DISPATCH[m["endpoint"]](req)
    new_hash = sha256_of(result)
    return {"run_id": run_id, "reproduced": new_hash == m["result_hash"], "original_hash": m["result_hash"],
            "replay_hash": new_hash}
