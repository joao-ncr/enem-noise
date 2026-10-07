"""Confiabilidade e concordância entre avaliadores.

Como os avaliadores são sorteados independentemente para cada redação (não há avaliadores 'cruzados'),
o desenho é de ANOVA de um fator (redação) e o ICC adequado é o ICC(1,1)/ICC(1,k).
Separação conceitual mantida: variância entre redações (desempenho real) x variância do erro de avaliação.
"""
from __future__ import annotations

import numpy as np


def icc_oneway(x: np.ndarray) -> dict:
    """x: (n_redações, k_avaliações). Retorna ICC(1,1), ICC(1,k), componentes de variância e SEM."""
    x = np.asarray(x, dtype=float)
    n, k = x.shape
    gm = x.mean()
    ms_b = k * ((x.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    ms_w = ((x - x.mean(axis=1, keepdims=True)) ** 2).sum() / (n * (k - 1))
    var_e = ms_w
    var_t = max((ms_b - ms_w) / k, 0.0)
    icc1 = (ms_b - ms_w) / (ms_b + (k - 1) * ms_w)
    icck = (ms_b - ms_w) / ms_b
    sd_obs = x.std(ddof=1)
    return {"icc_1_1": float(icc1), "icc_1_k": float(icck), "var_true": float(var_t), "var_error": float(var_e),
            "var_observed_single": float(var_t + var_e), "sem": float(np.sqrt(var_e)),
            "sem_from_icc": float(sd_obs * np.sqrt(max(1 - icc1, 0))), "n": int(n), "k": int(k)}


def bland_altman(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.asarray(a, float) - np.asarray(b, float)
    m, s = float(d.mean()), float(d.std(ddof=1))
    return {"bias": m, "sd_diff": s, "loa_low": m - 1.96 * s, "loa_high": m + 1.96 * s,
            "mean_abs_diff": float(np.abs(d).mean())}


def weighted_kappa_quadratic(a: np.ndarray, b: np.ndarray, n_levels: int = 6) -> float:
    a = np.asarray(a, int); b = np.asarray(b, int)
    O = np.zeros((n_levels, n_levels))
    np.add.at(O, (a, b), 1)
    O /= O.sum()
    ra, rb = O.sum(1), O.sum(0)
    E = np.outer(ra, rb)
    i = np.arange(n_levels)
    W = (i[:, None] - i[None, :]) ** 2 / (n_levels - 1) ** 2
    den = (W * E).sum()
    return float(1 - (W * O).sum() / den) if den > 0 else float("nan")


def reliability_report(s1: np.ndarray, s2: np.ndarray, step: float = 40.0) -> dict:
    """s1, s2: (N,5) pontos de dois avaliadores sobre N redações DISTINTAS."""
    out = {"total": {**icc_oneway(np.stack([s1.sum(1), s2.sum(1)], axis=1)),
                     "bland_altman": bland_altman(s1.sum(1), s2.sum(1))}}
    for c in range(s1.shape[1]):
        r = icc_oneway(np.stack([s1[:, c], s2[:, c]], axis=1))
        r["bland_altman"] = bland_altman(s1[:, c], s2[:, c])
        lv1, lv2 = np.rint(s1[:, c] / step).astype(int), np.rint(s2[:, c] / step).astype(int)
        if np.allclose(s1[:, c], lv1 * step) and np.allclose(s2[:, c], lv2 * step):
            r["kappa_quadratico"] = weighted_kappa_quadratic(np.clip(lv1, 0, 5), np.clip(lv2, 0, 5))
        out[f"C{c + 1}"] = r
    return out
