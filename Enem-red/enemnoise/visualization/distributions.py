from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

from .common import plt, save, stamp


def plot_distribution(final: np.ndarray, path, title: str, provenance: str, latent: Optional[float] = None,
                      cutoffs: Sequence[float] = ()):
    fig, ax = plt.subplots(figsize=(8, 4))
    step = 20
    edges = np.arange(final.min() - step / 2, final.max() + step, step)
    ax.hist(final, bins=edges, weights=np.full(final.size, 1 / final.size), color="#3b82c4", edgecolor="white")
    if latent is not None:
        ax.axvline(latent, color="k", ls="--", label=f"T* latente = {latent:.0f}")
    for c in cutoffs:
        ax.axvline(c, color="#d33", ls=":", label=f"corte {c:g}")
    ax.set(xlabel="Nota final da redação", ylabel="Frequência relativa", title=title)
    ax.legend(fontsize=8)
    return save(stamp(fig, provenance), path)


def plot_boxplot(groups: Dict[str, np.ndarray], path, title: str, provenance: str):
    fig, ax = plt.subplots(figsize=(max(6, 1.2 * len(groups)), 4))
    ax.boxplot(list(groups.values()), tick_labels=list(groups.keys()), showfliers=False)
    ax.set(ylabel="Nota final", title=title)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    return save(stamp(fig, provenance), path)


def plot_density_overlap(fa: np.ndarray, fb: np.ndarray, la: str, lb: str, path, provenance: str, overlap=None):
    fig, ax = plt.subplots(figsize=(8, 4))
    step = 20
    lo, hi = min(fa.min(), fb.min()), max(fa.max(), fb.max())
    edges = np.arange(lo - step / 2, hi + step, step)
    for f, lab, col in ((fa, la, "#3b82c4"), (fb, lb, "#e0802d")):
        ax.hist(f, bins=edges, weights=np.full(f.size, 1 / f.size), alpha=0.55, label=lab, color=col)
    ttl = "Sobreposição das distribuições" + (f" (coef. = {overlap:.2f})" if overlap is not None else "")
    ax.set(xlabel="Nota final", ylabel="Frequência relativa", title=ttl)
    ax.legend()
    return save(stamp(fig, provenance), path)


def plot_heatmap(data: np.ndarray, rows: Sequence[str], cols: Sequence[str], path, title: str, provenance: str,
                 cbar_label: str = "DP da nota final (pts)"):
    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(cols)), [f"{c:g}" for c in cols])
    ax.set_yticks(range(len(rows)), rows)
    ax.set(xlabel="sigma da competência (níveis)", title=title)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, label=cbar_label)
    return save(stamp(fig, provenance), path)
