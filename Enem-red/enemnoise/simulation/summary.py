"""Estatísticas descritivas de um lote de correções."""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

QUANTILES = (2.5, 25, 50, 75, 97.5)
DEFAULT_BANDS = (0, 200, 400, 500, 600, 700, 800, 900, 1000.0001)
ERR_THRESHOLD = 40.0


def to_jsonable(o):
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return to_jsonable(o.tolist())
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def frequency_table(final: np.ndarray, step: float = 20.0, max_bins: int = 60) -> dict:
    """Distribuição de frequência: valores discretos (múltiplos de `step`) ou histograma contínuo."""
    f = np.asarray(final, dtype=float)
    on_grid = np.allclose(f, np.round(f / step) * step)
    if on_grid:
        vals, cnt = np.unique(np.round(f / step) * step, return_counts=True)
        return {"kind": "discrete", "values": vals.tolist(), "probs": (cnt / f.size).tolist()}
    cnt, edges = np.histogram(f, bins=max_bins, range=(0, 1000))
    return {"kind": "histogram", "edges": edges.tolist(), "probs": (cnt / f.size).tolist()}


def summarize(batch, latent_total: Optional[float], cutoffs: Sequence[float] = (),
              bands: Sequence[float] = DEFAULT_BANDS, err_threshold: float = ERR_THRESHOLD) -> dict:
    f = batch.final.astype(float)
    n = f.size
    mean, sd = float(f.mean()), float(f.std(ddof=1)) if n > 1 else 0.0
    se = sd / np.sqrt(n)
    out = {
        "n": n, "mean": mean, "median": float(np.median(f)), "std": sd, "variance": sd ** 2,
        "min": float(f.min()), "max": float(f.max()),
        "mc_se_mean": float(se), "ci95_mean": [mean - 1.96 * se, mean + 1.96 * se],
        "quantiles": {str(q): float(np.percentile(f, q)) for q in QUANTILES},
        "p_third_rater": float(batch.third.mean()), "p_banca": float(batch.banca.mean()),
    }
    gap = np.abs(batch.s1.sum(axis=1) - batch.s2.sum(axis=1))
    out["rater_gap"] = {"mean_abs_total_diff": float(gap.mean()), "p95_total_diff": float(np.percentile(gap, 95)),
                        "p_gt_100": float((gap > 100).mean()), "p_gt_0": float((gap > 0).mean())}
    # bandas
    counts, _ = np.histogram(f, bins=list(bands))
    out["band_probs"] = {f"[{bands[i]:g},{min(bands[i + 1], 1000):g}]": float(counts[i] / n) for i in range(len(counts))}
    # separação viés x ruído
    noise = f - mean
    out["noise_only"] = {"p_abs_dev_ge_threshold": float((np.abs(noise) >= err_threshold).mean()),
                         "threshold": err_threshold}
    if latent_total is not None:
        err = f - latent_total
        out["vs_latent"] = {"latent_total": float(latent_total), "bias": float(err.mean()),
                            "rmse": float(np.sqrt((err ** 2).mean())),
                            "p_abs_err_ge_threshold": float((np.abs(err) >= err_threshold).mean()),
                            "threshold": err_threshold}
    cut = {}
    for c in cutoffs:
        p = float((f >= c).mean())
        entry = {"p_ge": p, "mc_se": float(np.sqrt(p * (1 - p) / n))}
        if latent_total is not None:
            above = latent_total >= c
            entry["latent_side"] = "acima" if above else "abaixo"
            entry["p_misclassified_vs_latent"] = float(1 - p if above else p)
        cut[str(c)] = entry
    out["classification_impact"] = cut
    out["distribution"] = frequency_table(f)
    return to_jsonable(out)
