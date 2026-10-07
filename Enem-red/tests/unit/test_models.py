import numpy as np
import pytest

from enemnoise.models.competency import NoiseParams
from enemnoise.models.essay import Essay, latent_total
from enemnoise.models.evaluator import Panel
from enemnoise.models.provenance import Provenance, combine, result_label
from enemnoise.simulation.distributions import MODELS, get_model


def test_discretizacao_m1_bordas():
    m = MODELS["M1"]
    y = np.array([[-1.0, 0.49, 0.5, 1.49, 2.5, 4.49, 4.5, 9.0]])
    assert m.to_points(y).tolist() == [[0, 0, 40, 40, 120, 160, 200, 200]]


def test_m0_trunca():
    assert MODELS["M0"].to_points(np.array([[-1.0, 2.5, 7.0]])).tolist() == [[0.0, 100.0, 200.0]]


def test_modelo_desconhecido():
    with pytest.raises(ValueError):
        get_model("X")


def test_latent_total_e_essay():
    e = Essay.from_points("a", [160, 160, 160, 160, 160])
    assert e.latent_total == 800.0
    assert latent_total([7, 7, 7, 7, 7]) == 1000.0
    with pytest.raises(ValueError):
        Essay("x", (1, 2))
    assert e.with_delta({2: 0.5}).latent_total == 820.0


def test_noise_params_validacao():
    with pytest.raises(ValueError):
        NoiseParams(sigma_c=(0.1,) * 4)
    with pytest.raises(ValueError):
        NoiseParams.uniform(-0.1)
    assert NoiseParams.from_dict({"sigma": 0.3}).sigma_c == (0.3,) * 5


def test_painel():
    p = Panel.preset("misto")
    assert len(p.profiles) == 2 and abs(p.weights.sum() - 1) < 1e-12
    with pytest.raises(ValueError):
        Panel.preset("inexistente")
    assert Panel.from_dict(p.to_dict()).name == "misto"


def test_proveniencia_herda_pior_rotulo():
    assert combine(Provenance.OBSERVADO, Provenance.HIPOTETICO) == Provenance.HIPOTETICO
    assert "HIPOTÉTICOS" in result_label([Provenance.ESTIMADO, Provenance.HIPOTETICO])
    assert result_label([Provenance.OBSERVADO]) == "SIMULADO"
