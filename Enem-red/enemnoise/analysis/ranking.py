"""Experimento de ranking: ordenação latente x ordenação observada."""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy import stats

from ..models.competency import MAX_LEVEL, STEP
from ..models.essay import latent_total
from ..simulation.engine import SimulationEngine
from ..simulation.summary import to_jsonable


def observed_finals(engine: SimulationEngine, theta: np.ndarray, replicates: int, seed: int) -> np.ndarray:
    """Cada replicação corrige TODAS as M redações com novos avaliadores -> (R, M)."""
    m = theta.shape[0]
    rows = np.tile(theta, (replicates, 1))
    return engine.grade_chunked(rows, seed).final.reshape(replicates, m)


def inversion_counts(latent: np.ndarray, obs: np.ndarray, min_gap: float = 0.0):
    """Para um vetor observado (M,): pares com latente_a > latente_b + min_gap.
    Retorna (n_pares, n_inversões_estritas, n_empates, matriz_gap_apenas_por_amostragem)."""
    d_lat = latent[:, None] - latent[None, :]
    d_obs = obs[:, None] - obs[None, :]
    mask = d_lat > min_gap
    return int(mask.sum()), int((mask & (d_obs < 0)).sum()), int((mask & (d_obs == 0)).sum())


def inversion_by_gap(latent, obs_matrix, gap_edges=(0, 10, 20, 40, 80, 160, 1000), max_pairs=400_000, rng=None):
    """P(inversão) em função da diferença latente (em pontos) — curva dose-resposta."""
    rng = rng or np.random.default_rng(0)
    m = latent.size
    ia, ib = np.triu_indices(m, 1)
    if ia.size > max_pairs:
        sel = rng.choice(ia.size, max_pairs, replace=False)
        ia, ib = ia[sel], ib[sel]
    swap = latent[ia] < latent[ib]
    ia2, ib2 = np.where(swap, ib, ia), np.where(swap, ia, ib)   # a = maior latente
    gap = latent[ia2] - latent[ib2]
    inv = (obs_matrix[:, ia2] < obs_matrix[:, ib2]).mean(axis=0)
    tie = (obs_matrix[:, ia2] == obs_matrix[:, ib2]).mean(axis=0)
    rows = []
    for lo, hi in zip(gap_edges[:-1], gap_edges[1:]):
        s = (gap > lo) & (gap <= hi)
        if s.any():
            rows.append({"gap_lo": lo, "gap_hi": hi, "n_pairs": int(s.sum()),
                         "p_inversion": float(inv[s].mean()), "p_tie": float(tie[s].mean())})
    return rows


def ranking_experiment(engine: SimulationEngine, theta: np.ndarray, replicates: int, seed: int,
                       top_fraction: float = 0.2, min_gap: float = 0.0) -> dict:
    latent = latent_total(theta)
    obs = observed_finals(engine, theta, replicates, seed)
    m = latent.size
    sp = np.array([stats.spearmanr(latent, o)[0] for o in obs])
    kt = np.array([stats.kendalltau(latent, o)[0] for o in obs])
    r_lat = stats.rankdata(-latent)
    disp = np.zeros(m)
    inv_tot = pairs_tot = ties_tot = 0
    for o in obs:
        disp += np.abs(stats.rankdata(-o) - r_lat)
        if m <= 2000:
            p, i, t = inversion_counts(latent, o, min_gap)
            pairs_tot += p; inv_tot += i; ties_tot += t
    disp /= replicates
    # classificação: topo top_fraction pela ordem latente vs observada
    k = max(1, int(round(top_fraction * m)))
    top_lat = np.zeros(m, bool); top_lat[np.argsort(-latent)[:k]] = True
    flips = []
    for o in obs:
        top_obs = np.zeros(m, bool); top_obs[np.argsort(-o, kind="stable")[:k]] = True
        flips.append((top_obs != top_lat).sum() / 2.0)      # nº de candidatos trocados entre dentro/fora
    most = np.argsort(-disp)[:10]
    base_inv = None
    if engine.model.discrete and m <= 2000:
        # linha de base: avaliador perfeito e sem ruído, só a discretização em 6 níveis por competência
        obs0 = (STEP * np.clip(np.floor(theta + 0.5), 0, MAX_LEVEL)).sum(axis=1)
        p0, i0, t0 = inversion_counts(latent, obs0, min_gap)
        base_inv = {"p_inversion": i0 / p0 if p0 else 0.0, "p_tie": t0 / p0 if p0 else 0.0}
    out = {
        "n_essays": m, "replicates": replicates,
        "spearman_mean": float(sp.mean()), "spearman_ci95": [float(np.percentile(sp, 2.5)), float(np.percentile(sp, 97.5))],
        "kendall_mean": float(kt.mean()),
        "mean_abs_rank_displacement": float(disp.mean()), "max_mean_rank_displacement": float(disp.max()),
        "most_affected": [{"index": int(i), "latent_total": float(latent[i]), "mean_abs_rank_shift": float(disp[i])} for i in most],
        "top_fraction": top_fraction, "top_k": k,
        "mean_swaps_in_out_of_top": float(np.mean(flips)),
        "frac_of_top_replaced": float(np.mean(flips) / k),
    }
    if pairs_tot:
        out.update({"n_pairs_per_replicate": pairs_tot // replicates,
                    "p_inversion_all_pairs": inv_tot / pairs_tot, "p_tie_all_pairs": ties_tot / pairs_tot,
                    "mean_inversions_per_replicate": inv_tot / replicates})
        out["inversion_by_gap"] = inversion_by_gap(latent, obs)
    out["discretization_only_baseline"] = base_inv
    out["_arrays"] = {"latent": latent, "obs_mean": obs.mean(axis=0), "obs_first": obs[0], "disp": disp}
    return out


def public_ranking_result(res: dict) -> dict:
    return to_jsonable({k: v for k, v in res.items() if k != "_arrays"})
