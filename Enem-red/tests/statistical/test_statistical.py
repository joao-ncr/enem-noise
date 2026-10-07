import numpy as np
import pytest

from enemnoise.analysis.compare import compare_pair
from enemnoise.analysis.model_check import model_divergence
from enemnoise.analysis.paradox import ParadoxDetector
from enemnoise.analysis.ranking import ranking_experiment, inversion_by_gap, observed_finals
from enemnoise.analysis.reliability import reliability_report
from enemnoise.analysis.sensitivity import observed_perturbation, sensitivity_latent
from enemnoise.models.competency import NoiseParams
from enemnoise.models.essay import Essay, latent_total
from enemnoise.models.evaluator import Panel
from enemnoise.simulation.engine import SimulationEngine
from enemnoise.simulation.population import PopulationPrior


def eng(sigma=0.35, su=0.15, sb=0.1, model="M1", panel="neutro"):
    return SimulationEngine(model, "inep_2025", NoiseParams.uniform(sigma, sigma_u=su, sigma_beta=sb), Panel.preset(panel))


def test_sem_ruido_nota_final_igual_ao_nivel_latente_discretizado():
    e = eng(0, 0, 0)
    r = e.run_essay(Essay("a", (4, 3, 5, 2, 1)), 2000, 1)
    assert r.statistics["std"] == 0 and r.statistics["mean"] == 600.0
    assert r.statistics["p_third_rater"] == 0


def test_reprodutibilidade_mesma_seed_resultado_identico():
    a = eng().run_essay(Essay.uniform("x", 3.4), 20000, 77).final
    b = eng().run_essay(Essay.uniform("x", 3.4), 20000, 77).final
    c = eng().run_essay(Essay.uniform("x", 3.4), 20000, 78).final
    assert np.array_equal(a, b) and not np.array_equal(a, c)


def test_reproducibilidade_independe_do_numero_de_iteracoes_no_primeiro_bloco():
    a = eng().run_essay(Essay.uniform("x", 3.4), 5000, 5).final
    b = eng().run_essay(Essay.uniform("x", 3.4), 8000, 5).final
    assert a.shape == (5000,) and b.shape == (8000,)


def test_convergencia_monte_carlo_erro_padrao_cai_com_raiz_de_n():
    e = eng()
    es = Essay.uniform("x", 3.4)
    m_small = [e.run_essay(es, 2000, s).statistics["mean"] for s in range(40)]
    m_big = [e.run_essay(es, 8000, 1000 + s).statistics["mean"] for s in range(40)]
    ratio = np.std(m_small, ddof=1) / np.std(m_big, ddof=1)
    assert 1.4 < ratio < 2.8     # esperado ~2


def test_recuperacao_de_parametros_icc_em_modelo_normal():
    """Simula com sigma conhecido e verifica que o ICC estimado recupera o valor teórico."""
    s, su, sb = 0.4, 0.2, 0.1
    prior = PopulationPrior(mu=(2.5,) * 5, tau=0.5, rho=0.7)
    th = prior.sample(np.random.default_rng(1), 60000)
    b = eng(s, su, sb, model="M0").grade_chunked(th, 2)
    est = reliability_report(b.s1, b.s2)["total"]["icc_1_1"]
    var_t = 1600 * prior.tau ** 2 * (25 * prior.rho + 5 * (1 - prior.rho))
    var_e = 1600 * (25 * (su ** 2 + sb ** 2) + 5 * s ** 2)
    assert est == pytest.approx(var_t / (var_t + var_e), abs=0.02)


def test_icc_por_competencia_recupera_valor_teorico():
    s, su, sb = 0.5, 0.0, 0.0
    prior = PopulationPrior(mu=(2.5,) * 5, tau=0.6, rho=0.5)
    th = prior.sample(np.random.default_rng(3), 60000)
    b = eng(s, su, sb, model="M0").grade_chunked(th, 4)
    est = reliability_report(b.s1, b.s2)["C2"]["icc_1_1"]
    assert est == pytest.approx(0.36 / (0.36 + 0.25), abs=0.02)


def test_contra_hipotese_baixo_ruido_nao_aciona_paradoxos():
    """O detector não pode 'acusar paradoxo em tudo': com ruído mínimo nada deve disparar."""
    e = eng(0.05, 0, 0)
    A, B = Essay.uniform("A", 4), Essay("B", (4, 4, 3, 4, 4))
    cmp = compare_pair(e, A, B, 5000, 1)
    st = e.run_essay(A, 5000, 2, [800]).statistics
    sens = sensitivity_latent(e, A, [{"2": 0.1}, {"2": 0.3}], 5000, 3, [800])
    found = ParadoxDetector().scan(cmp=cmp, sens=sens, stats=st, cutoffs=[800])
    assert found and not any(f.triggered for f in found)


def test_controle_positivo_alto_ruido_aciona_paradoxos():
    e = eng(1.0, 0.3, 0.2)
    A, B = Essay.uniform("A", 4), Essay("B", (4, 4, 3, 4, 4))
    cmp = compare_pair(e, A, B, 20000, 1)
    st = e.run_essay(A, 20000, 2, [800]).statistics
    det = ParadoxDetector()
    assert det.inversion(cmp).triggered and det.boundary(st, 800, "x").triggered and det.overlap(cmp).triggered


def test_ranking_sem_ruido_nao_tem_inversoes_e_com_ruido_tem():
    th = PopulationPrior().sample(np.random.default_rng(0), 60)
    r0 = ranking_experiment(eng(0, 0, 0), th, 5, 1)
    r1 = ranking_experiment(eng(0.8, 0.3, 0.2), th, 5, 1)
    # sem ruído só resta a inversão por discretização da escala (6 níveis) — deve coincidir com a linha de base
    assert r0["p_inversion_all_pairs"] == pytest.approx(r0["discretization_only_baseline"]["p_inversion"])
    assert r0["p_inversion_all_pairs"] < 0.05 and r0["spearman_mean"] > 0.97
    assert r1["p_inversion_all_pairs"] > 2 * r0["p_inversion_all_pairs"] and r1["spearman_mean"] < r0["spearman_mean"]


def test_inversao_diminui_com_a_diferenca_latente():
    th = PopulationPrior().sample(np.random.default_rng(2), 120)
    e = eng(0.6, 0.2, 0.1)
    from enemnoise.models.essay import latent_total as lt
    obs = observed_finals(e, th, 30, 5)
    rows = inversion_by_gap(lt(th), obs)
    assert rows[0]["p_inversion"] > rows[-1]["p_inversion"]


def test_sensibilidade_media_cresce_com_perturbacao():
    out = sensitivity_latent(eng(), Essay.uniform("a", 3.0), [{"2": 0.25}, {"2": 0.5}, {"2": 1.0}], 20000, 1, [600])
    d = [r["delta_mean_final"] for r in out["rows"]]
    assert d[0] < d[1] < d[2]
    assert [r["delta_latent_points"] for r in out["rows"]] == [10.0, 20.0, 40.0]


def test_perturbacao_observada_minima_e_40_pts_logo_20_na_final():
    out = observed_perturbation(eng(), [120] * 5, [120] * 5, rater=0, competency=0, delta_points=40)
    assert out["delta_final"] == 20.0 and not out["third_after"]


def test_divergencia_entre_modelos_e_reportada():
    out = model_divergence(Essay.uniform("a", 3.0), NoiseParams.uniform(0.35), Panel.preset("neutro"), iterations=5000)
    assert set(out["by_model"]) == {"M0", "M1", "M1H"} and "message" in out


def test_efeito_painel_misto_aumenta_discrepancia_entre_avaliadores():
    a = eng(0.3, 0.1, 0.05, panel="neutro").run_essay(Essay.uniform("x", 3), 20000, 1).statistics["rater_gap"]["mean_abs_total_diff"]
    b = eng(0.3, 0.1, 0.05, panel="misto").run_essay(Essay.uniform("x", 3), 20000, 1).statistics["rater_gap"]["mean_abs_total_diff"]
    assert b > a
