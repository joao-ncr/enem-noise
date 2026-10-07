import numpy as np
from hypothesis import given, settings, strategies as st

from enemnoise.analysis.compare import compare_pair
from enemnoise.models.competency import NoiseParams
from enemnoise.models.essay import Essay
from enemnoise.models.evaluator import Panel
from enemnoise.simulation.engine import SimulationEngine

level = st.floats(min_value=0.0, max_value=5.0, allow_nan=False)


def eng(model="M1", sigma=0.4):
    return SimulationEngine(model, "inep_2025", NoiseParams.uniform(sigma), Panel.preset("misto"))


@settings(max_examples=15, deadline=None)
@given(st.lists(level, min_size=5, max_size=5), st.sampled_from(["M0", "M1", "M1H"]))
def test_nota_sempre_entre_0_e_1000(theta, model):
    r = eng(model).run_essay(Essay("e", tuple(theta)), 1000, 3)
    assert r.final.min() >= 0 and r.final.max() <= 1000


@settings(max_examples=12, deadline=None)
@given(st.lists(level, min_size=5, max_size=5), st.lists(level, min_size=5, max_size=5))
def test_simetria_e_soma_das_probabilidades(ta, tb):
    e = eng()
    c1 = compare_pair(e, Essay("A", tuple(ta)), Essay("B", tuple(tb)), 2000, 5)
    assert abs(c1["p_a_gt_b"] + c1["p_b_gt_a"] + c1["p_tie"] - 1) < 1e-9
    assert 0 <= c1["overlap_coefficient"] <= 1.0000001


@settings(max_examples=10, deadline=None)
@given(st.floats(min_value=1.0, max_value=3.5))
def test_monotonicidade_na_media(base):
    e = eng()
    lo = e.run_essay(Essay.uniform("lo", base), 4000, 9).statistics["mean"]
    hi = e.run_essay(Essay.uniform("hi", base + 1.0), 4000, 9).statistics["mean"]
    assert hi > lo


@settings(max_examples=10, deadline=None)
@given(st.lists(level, min_size=5, max_size=5))
def test_final_em_multiplos_de_20_no_modelo_discreto(theta):
    r = eng("M1").run_essay(Essay("e", tuple(theta)), 1000, 4)
    assert np.allclose(r.final % 20, 0)
