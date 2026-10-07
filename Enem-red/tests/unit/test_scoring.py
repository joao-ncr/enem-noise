import numpy as np
import pytest

from enemnoise.simulation.scoring import RULES, consolidate, is_discrepant


def arr(*rows):
    return np.array(rows, dtype=float)


def test_discrepancia_total_exatamente_100_nao_e_discrepante_na_regra_estrita():
    a = arr([120, 120, 120, 120, 120])
    b = arr([160, 160, 160, 120, 120]) # dif total = 120 -> discrepante
    c = arr([120, 120, 120, 120, 120]) + np.array([[20, 20, 20, 20, 20]])  # dif total = 100, cada comp = 20
    assert not is_discrepant(RULES["inep_2025"], a, c)[0]
    assert is_discrepant(RULES["inep_2025_inclusive"], a, c)[0]
    assert is_discrepant(RULES["inep_2025"], a, b)[0]


def test_discrepancia_total_101():
    a = arr([100, 100, 100, 100, 100])
    b = a + np.array([[21, 20, 20, 20, 20]])
    assert is_discrepant(RULES["inep_2025"], a, b)[0]


def test_discrepancia_por_competencia_80_vs_81():
    a = arr([100, 100, 100, 100, 100])
    b80 = arr([180, 100, 100, 100, 100])   # 80 em uma competência; total 80 <= 100
    b81 = arr([181, 100, 100, 100, 100])
    assert not is_discrepant(RULES["inep_2025"], a, b80)[0]
    assert is_discrepant(RULES["inep_2025"], a, b81)[0]


def test_media_simples_sem_discrepancia():
    s1 = arr([120, 120, 120, 120, 120]); s2 = arr([160, 120, 120, 120, 120])
    fc, third, banca = consolidate(RULES["inep_2025"], s1, s2, lambda i: s1[i], lambda i: np.stack([s1[i]] * 3, 1))
    assert fc.sum() == 620 and not third[0] and not banca[0]


def test_terceiro_corretor_media_das_duas_mais_proximas():
    s1 = arr([200, 200, 200, 200, 200])      # 1000
    s2 = arr([100, 100, 100, 100, 100])      # 500 -> discrepante
    s3 = arr([180, 180, 180, 180, 180])      # 900: converge com s1 (dif 100, cada comp 20), diverge de s2
    fc, third, banca = consolidate(RULES["inep_2025"], s1, s2, lambda i: s3[i * 0], lambda i: None)
    assert third[0] and not banca[0]
    assert fc.sum() == pytest.approx(950.0)   # média de 1000 e 900


def test_terceiro_diverge_dos_dois_aciona_banca():
    s1 = arr([200, 200, 200, 200, 200]); s2 = arr([0, 0, 0, 0, 0])
    s3 = arr([100, 100, 100, 100, 100])
    banca = lambda i: np.stack([np.tile(arr([120, 120, 120, 120, 120]), (len(i), 1))] * 3, 1)
    fc, third, bc = consolidate(RULES["inep_2025"], s1, s2, lambda i: s3[i * 0], banca)
    assert third[0] and bc[0] and fc.sum() == 600


def test_regra_simple_mean_nunca_aciona_terceiro():
    s1 = arr([200] * 5); s2 = arr([0] * 5)
    fc, third, banca = consolidate(RULES["simple_mean"], s1, s2, lambda i: s1[i], None)
    assert fc.sum() == 500 and not third.any()
