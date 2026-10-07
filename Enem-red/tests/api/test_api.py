import pytest
from fastapi.testclient import TestClient

from enemnoise.api.app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ENEM_NOISE_DATA_DIR", str(tmp_path))
    return TestClient(app)


def test_simulate_basico_e_rotulos(client):
    r = client.post("/simulate", json={"essay_profile": {"theta": [4] * 5}, "iterations": 3000, "cutoffs": [800], "return_scores": 5})
    assert r.status_code == 200
    j = r.json()
    assert "HIPOTÉTICOS" in j["provenance"] and "SIMULADO" in j["provenance"]
    assert len(j["scores"]) == 5 and j["classification_impact"]["800.0"]["p_ge"] > 0
    for k in ("seed", "timestamp_utc", "model_version", "data_version", "config_hash"):
        assert k in j["run_manifest"]


def test_replay_reproduz_exatamente(client):
    j = client.post("/simulate", json={"essay_profile": {"theta": [3.3] * 5}, "iterations": 3000}).json()
    rid = j["run_manifest"]["run_id"]
    assert client.get(f"/runs/{rid}").status_code == 200
    assert client.post(f"/runs/{rid}/replay").json()["reproduced"] is True
    assert client.post("/runs/nao-existe/replay").status_code == 404


def test_compare_e_paradoxos(client):
    r = client.post("/compare", json={"essays": [{"id": "A", "theta": [4] * 5}, {"id": "B", "theta": [4, 4, 3, 4, 4]}], "iterations": 4000})
    p = r.json()["pairs"][0]
    assert p["latent_order"] == "A>B" and 0 <= p["p_ranking_inversion"] <= 1 and len(p["paradoxes"]) == 2


def test_sensitivity(client):
    r = client.post("/sensitivity", json={"essay_profile": {"theta": [3] * 5}, "perturbations": [{"2": 0.25}, {"2": 1.0}],
                                          "cutoffs": [600], "iterations": 4000})
    assert r.status_code == 200 and len(r.json()["rows"]) == 2


def test_scenarios(client):
    names = client.get("/scenario").json()
    assert "notas_proximas" in names and "fronteira_classificatoria" in names
    for n in ("notas_proximas", "painel_misto"):
        assert client.post("/scenario", json={"name": n, "iterations": 2000}).status_code == 200
    assert client.post("/scenario", json={"name": "xx", "iterations": 2000}).status_code == 422


def test_validacao(client):
    assert client.post("/simulate", json={"essay_profile": {"theta": [1]}}).status_code == 422
    assert client.post("/simulate", json={"essay_profile": {"theta": [3] * 5}, "model": "X", "iterations": 1000}).status_code == 422
    assert client.get("/meta").json()["provenance_levels"][0] == "OBSERVADO"
