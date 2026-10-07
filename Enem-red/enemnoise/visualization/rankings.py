from __future__ import annotations

import numpy as np
from scipy import stats

from .common import plt, save, stamp


def plot_latent_vs_observed(latent, observed, path, provenance: str, title="Desempenho latente × nota observada"):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(latent, observed, s=8, alpha=0.5)
    lim = [min(latent.min(), observed.min()), max(latent.max(), observed.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set(xlabel="T* latente (pts)", ylabel="Nota observada (pts)", title=title)
    return save(stamp(fig, provenance), path)


def plot_rank_vs_rank(latent, observed, path, provenance: str):
    rl, ro = stats.rankdata(-latent), stats.rankdata(-observed)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(rl, ro, s=8, alpha=0.5)
    ax.plot([1, len(rl)], [1, len(rl)], "k--", lw=1)
    ax.set(xlabel="Ranking verdadeiro (latente)", ylabel="Ranking observado", title="Ranking verdadeiro × observado")
    return save(stamp(fig, provenance), path)


def plot_inversion_by_gap(rows, path, provenance: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [f"({r['gap_lo']:g},{r['gap_hi']:g}]" for r in rows]
    ax.bar(labels, [r["p_inversion"] for r in rows], color="#c0392b", label="inversão")
    ax.bar(labels, [r["p_tie"] for r in rows], bottom=[r["p_inversion"] for r in rows], color="#999", label="empate")
    ax.set(xlabel="Diferença latente entre as redações (pts)", ylabel="Probabilidade",
           title="P(inversão de ranking) por diferença real de desempenho")
    ax.legend()
    return save(stamp(fig, provenance), path)


def plot_frontier(latent, p_pass, cutoff, path, provenance: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(latent, p_pass, s=10, alpha=0.6)
    ax.axvline(cutoff, color="r", ls=":")
    ax.axhspan(0.05, 0.95, color="orange", alpha=0.12, label="zona de instabilidade (5%–95%)")
    ax.set(xlabel="T* latente (pts)", ylabel=f"P(nota ≥ {cutoff:g})", title="Fronteira classificatória")
    ax.legend()
    return save(stamp(fig, provenance), path)
