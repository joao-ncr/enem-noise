import numpy as np
import pandas as pd
import pytest

from enemnoise.providers.external import ExternalAPIDataProvider
from enemnoise.providers.real import RealDataProvider
from enemnoise.providers.simulated import SimulatedDataProvider
from enemnoise.registry import RunRegistry, sha256_of


def test_registry_roundtrip(tmp_path):
    reg = RunRegistry(tmp_path)
    m = reg.save("simulate", {"a": 1}, {"x": [1, 2]}, seed=7, iterations=10)
    assert reg.load(m["run_id"])["seed"] == 7 and reg.load_result(m["run_id"]) == {"x": [1, 2]}
    assert m["result_hash"] == sha256_of({"x": [1, 2]})
    for k in ("timestamp_utc", "model_version", "data_version", "config_hash", "iterations"):
        assert k in m
    with pytest.raises(FileNotFoundError):
        reg.load("nao-existe")


def test_real_provider_le_csv_de_microdados(tmp_path):
    rng = np.random.default_rng(0)
    n = 500
    df = pd.DataFrame({f"NU_NOTA_COMP{i}": rng.choice([0, 40, 80, 120, 160, 200], n) for i in range(1, 6)})
    df["NU_NOTA_REDACAO"] = df.sum(axis=1)
    df["TP_STATUS_REDACAO"] = 1
    p = tmp_path / "micro.csv"
    df.to_csv(p, sep=";", index=False, encoding="latin-1")
    t = RealDataProvider(str(p), "TESTE").calibration_target()
    assert t.provenance.name == "OBSERVADO" and t.comp_probs.shape == (5, 11)
    assert np.allclose(t.comp_probs.sum(axis=1), 1.0)


def test_real_provider_arquivo_ausente_orienta_usuario():
    with pytest.raises(FileNotFoundError, match="DADOS_NECESSARIOS"):
        RealDataProvider("/nao/existe.csv")


def test_external_provider_ainda_nao_implementado():
    with pytest.raises(NotImplementedError):
        ExternalAPIDataProvider("http://x").calibration_target()


def test_provedor_simulado_rotula_como_simulado():
    t = SimulatedDataProvider(n=2000).calibration_target()
    assert t.provenance.name == "SIMULADO" and "SINTÉTICO" in t.source
